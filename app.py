#!/usr/bin/env python3
import os
import time
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from threading import Thread
from dotenv import load_dotenv

from lib.folder_monitor import FolderMonitor
from lib.audio_processor import AudioProcessor
from lib.transcription import TranscriptionService
from lib.diarization import DiarizationService
from lib.scene_detection import SceneDetector
from lib.summary_generator import SummaryGenerator
from lib.file_registry import FileRegistry
from config import Config

load_dotenv()

def wait_for_file_complete(path, stable_secs=3, timeout=120):
    stable_count = 0
    last_size = -1
    for _ in range(timeout):
        try:
            cur_size = os.path.getsize(path)
            if cur_size == last_size:
                stable_count += 1
                if stable_count >= stable_secs:
                    return True
            else:
                stable_count = 0
                last_size = cur_size
        except OSError:
            pass
        time.sleep(1)
    return False

app = Flask(__name__)
app.config.from_object(Config)

# Ensure all output directories exist
for dir_path in [
    app.config["WATCH_FOLDER"],
    app.config["AUDIO_OUTPUT_DIR"],
    app.config["SCENE_OUTPUT_DIR"],
    app.config["SUMMARY_OUTPUT_DIR"],
]:
    os.makedirs(dir_path, exist_ok=True)

audio_processor = AudioProcessor(
    sample_rate=app.config["AUDIO_SAMPLE_RATE"],
    channels=app.config["AUDIO_CHANNELS"],
    audio_output_dir=app.config["AUDIO_OUTPUT_DIR"] # Pass the output directory
)
transcriber = TranscriptionService(api_key=app.config["OPENAI_API_KEY"])
diarizer = DiarizationService(auth_token=app.config["HUGGINGFACE_TOKEN"])
scene_detector = SceneDetector()
summarizer = SummaryGenerator(api_key=app.config["OPENAI_API_KEY"])
file_registry = FileRegistry()

class MediaProcessor:
    def __init__(self):
        self.results = []
        self.processing_status = {}

    def run(self, file_path: str) -> None:
        job_id = os.path.basename(file_path)
        # --- Duplicate check ---
        if file_registry.is_already_processed(file_path):
            self.results.append({
                "file": file_path,
                "status": "duplicate",
                "message": "Already processed, skipping."
            })
            return

        self.processing_status[job_id] = {
            'status': 'processing',
            'stage': 'starting',
            'progress': 0,
            'file': file_path
        }
        
        # Register file as processing
        file_registry.register_file(file_path, status='processing')
        
        try:
            record = self._process_file(file_path)
            self.results.append(record)
            self.processing_status[job_id]['status'] = 'completed'
            self.processing_status[job_id]['progress'] = 100
            
            # Update to completed with result path
            result_path = record.get('summary_file', '')
            file_registry.update_file_status(
                file_registry.calculate_file_hash(file_path), 
                'completed', 
                result_path
            )
            
        except Exception as exc:
            self.processing_status[job_id]['status'] = 'error'
            self.processing_status[job_id]['error'] = str(exc)
            self.results.append({
                "file": file_path,
                "status": "error",
                "message": str(exc),
            })
            
            # Update to error status
            file_registry.update_file_status(
                file_registry.calculate_file_hash(file_path), 
                'error'
            )

    def _process_file(self, file_path: str) -> dict:
        job_id = os.path.basename(file_path)
        self.processing_status[job_id]['stage'] = 'extracting_audio'
        self.processing_status[job_id]['progress'] = 20

        if AudioProcessor.is_video(file_path):
            audio_wav = audio_processor.extract_audio(file_path)
            scenes, keyframes = scene_detector.detect_and_extract(
                video_path=file_path, output_dir=app.config["SCENE_OUTPUT_DIR"]
            )
        else:
            audio_wav = audio_processor.standardize_audio(file_path)
            scenes, keyframes = [], []

        self.processing_status[job_id]['stage'] = 'transcribing'
        self.processing_status[job_id]['progress'] = 40

        transcript_result = transcriber.transcribe(
            audio_wav, language=app.config["LANGUAGE"]
        )
        transcript_text = transcript_result["text"]
        self.processing_status[job_id]['stage'] = 'diarization'
        self.processing_status[job_id]['progress'] = 60

        diarization_rttm = diarizer.diarize(
            audio_wav,
            num_speakers=app.config["NUM_SPEAKERS"],
            output_dir=app.config["AUDIO_OUTPUT_DIR"],
        )

        self.processing_status[job_id]['stage'] = 'generating_summary'
        self.processing_status[job_id]['progress'] = 80

        summary_text = summarizer.generate(
            transcript=transcript_text, images=keyframes
        )

        summary_file = self._save_summary(file_path, summary_text)

        return {
            "file": file_path,
            "audio": audio_wav,
            "diarization": diarization_rttm,
            "scenes": scenes,
            "images": keyframes,
            "transcript": transcript_result,
            "summary_file": summary_file,
            "status": "completed",
        }

    def _save_summary(self, original_file: str, summary: str) -> str:
        base = os.path.basename(original_file)
        stem, _ = os.path.splitext(base)
        out_path = os.path.join(
            app.config["SUMMARY_OUTPUT_DIR"], f"{stem}_summary.txt"
        )
        with open(out_path, "w", encoding="utf-8") as fp:
            fp.write(summary)
        return out_path

processor = MediaProcessor()

# Global monitor instance (but not started)
folder_monitor = None
monitoring_active = False

def start_folder_monitoring(watch_path: str):
    """Start monitoring a specific folder."""
    global folder_monitor, monitoring_active
    
    if monitoring_active:
        stop_folder_monitoring()
    
    folder_monitor = FolderMonitor(
        watch_path=watch_path,
        callback=processor.run,
        supported_ext=Config.SUPPORTED_AUDIO + Config.SUPPORTED_VIDEO,
    )
    folder_monitor.start_async()
    monitoring_active = True
    return True

def stop_folder_monitoring():
    """Stop current folder monitoring."""
    global folder_monitor, monitoring_active
    
    if folder_monitor and monitoring_active:
        folder_monitor._observer.stop()
        folder_monitor._observer.join()
        monitoring_active = False
    return True


@app.route("/", methods=["GET"])
def dashboard():
    return render_template("dashboard.html", results=processor.results)

@app.route("/api/start", methods=["POST"])
def api_start():
    data = request.get_json(force=True)
    watch_dir = data.get("folder", "")
    if not watch_dir or not os.path.isdir(watch_dir):
        return jsonify({"error": "Invalid folder path"}), 400

    try:
        start_folder_monitoring(watch_dir)
        return jsonify({"message": f"Monitoring started for {watch_dir}"})
    except Exception as e:
        return jsonify({"error": f"Failed to start monitoring: {str(e)}"}), 500


@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file field"}), 400
    
    file = request.files["file"]
    filename = secure_filename(file.filename)
    
    # Use separate upload directory
    dest_dir = Config.UPLOAD_FOLDER  # Changed from WATCH_FOLDER
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, filename)
    file.save(dest)

    # Check for duplicates
    if file_registry.is_already_processed(dest):
        os.remove(dest)
        return jsonify({"message": "File already processed, skipping."}), 200

    def bg_process():
        if wait_for_file_complete(dest):
            processor.run(dest)
        else:
            print(f"File {dest} did not stabilize in time.")

    Thread(target=bg_process, daemon=True).start()
    return jsonify({"message": f"Uploaded {filename}. Processing will begin shortly."}), 201


@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        'processing': processor.processing_status,
        'results': processor.results
    })

@app.route("/api/status/<job_id>", methods=["GET"])
def api_job_status(job_id: str):
    if job_id in processor.processing_status:
        return jsonify(processor.processing_status[job_id])
    return jsonify({"error": "Job not found"}), 404

@app.route("/api/results/<int:item_id>", methods=["GET"])
def api_results(item_id: int):
    if 0 <= item_id < len(processor.results):
        return jsonify(processor.results[item_id])
    return jsonify({"error": "Not found"}), 404

@app.route("/api/stop", methods=["POST"])
def api_stop():
    try:
        stop_folder_monitoring()
        return jsonify({"message": "Monitoring stopped"})
    except Exception as e:
        return jsonify({"error": f"Failed to stop monitoring: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
