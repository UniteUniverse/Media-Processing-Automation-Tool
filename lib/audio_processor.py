"""Audio extraction and normalization."""
import subprocess
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

class AudioProcessor:
    """Handles audio tasks."""

    video_ext = (
        ".mp4",
        ".mov",
        ".mkv",
        ".avi",
        ".webm",
        ".flv",
        ".wmv",
    )

    def __init__(self, sample_rate: int = 16_000, channels: int = 1, audio_output_dir: str = None):
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_output_dir = audio_output_dir # Store the output directory

        if self.audio_output_dir:
            os.makedirs(self.audio_output_dir, exist_ok=True) # Ensure output dir exists

    # ------------------------------------------------------------------
    @staticmethod
    def is_video(path: str) -> bool:
        return path.lower().endswith(AudioProcessor.video_ext)

    # ------------------------------------------------------------------
    def extract_audio(self, video_path: str) -> str:
        """Return path to extracted WAV from video, saved to audio_output_dir."""
        stem = Path(video_path).stem # Get stem without suffix
        if not self.audio_output_dir:
            logging.warning("Audio output directory not set for AudioProcessor. Using video_path's directory.")
            out_path = Path(video_path).with_suffix(".wav").as_posix()
        else:
            out_path = Path(self.audio_output_dir) / f"{stem}.wav" # Save to dedicated output dir

        cmd = [
            "ffmpeg", "-y", "-i", video_path, "-vn",
            "-acodec", "pcm_s16le", "-ar", str(self.sample_rate),
            "-ac", str(self.channels), out_path.as_posix(),
        ]
        logging.info(f"FFmpeg command for extraction: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) # Capture stderr for debugging
        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg error: {e.stderr.decode()}")
            raise
        return out_path.as_posix()

    # ------------------------------------------------------------------
    def standardize_audio(self, audio_path: str) -> str:
        """Convert arbitrary audio to 16 kHz mono WAV, saved to audio_output_dir."""
        stem = Path(audio_path).stem
        if not self.audio_output_dir:
            logging.warning("Audio output directory not set for AudioProcessor. Using audio_path's directory.")
            out_path = Path(audio_path).with_suffix("_std.wav").as_posix()
        else:
            out_path = Path(self.audio_output_dir) / f"{stem}_std.wav" # Save to dedicated output dir

        cmd = [
            "ffmpeg", "-y", "-i", audio_path,
            "-acodec", "pcm_s16le", "-ar", str(self.sample_rate),
            "-ac", str(self.channels), out_path.as_posix(),
        ]
        logging.info(f"FFmpeg command for standardization: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg error: {e.stderr.decode()}")
            raise
        return out_path.as_posix()