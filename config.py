"""Shared settings for the Flask application."""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

class Config:  # pylint: disable=too-few-public-methods
    # -------------------------------------------------------------------------
    # API Keys
    # -------------------------------------------------------------------------
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY")
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "YOUR_HF_TOKEN")

    # -------------------------------------------------------------------------
    # Feature Settings
    # -------------------------------------------------------------------------
    LANGUAGE = os.getenv("LANGUAGE", "auto")  # en, ta, hi, or auto
    NUM_SPEAKERS = int(os.getenv("NUM_SPEAKERS", "0")) or None

    # -------------------------------------------------------------------------
    # Directories
    # -------------------------------------------------------------------------
    ROOT_DIR = Path(__file__).parent
    WATCH_FOLDER = os.getenv("WATCH_FOLDER", (ROOT_DIR / "input").resolve().as_posix())
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", (ROOT_DIR / "uploads").resolve().as_posix())
    AUDIO_OUTPUT_DIR = (ROOT_DIR / "processed" / "audio").as_posix()
    SCENE_OUTPUT_DIR = (ROOT_DIR / "processed" / "images").as_posix()
    SUMMARY_OUTPUT_DIR = (ROOT_DIR / "processed" / "summaries").as_posix()

    # -------------------------------------------------------------------------
    # Audio Processing
    # -------------------------------------------------------------------------
    AUDIO_SAMPLE_RATE = 16_000
    AUDIO_CHANNELS = 1

    # -------------------------------------------------------------------------
    # Supported Extensions
    # -------------------------------------------------------------------------
    SUPPORTED_AUDIO = (
        ".mp3",
        ".wav",
        ".flac",
        ".m4a",
        ".aac",
        ".ogg",
        ".wma",
    )
    SUPPORTED_VIDEO = (
        ".mp4",
        ".mov",
        ".mkv",
        ".avi",
        ".webm",
        ".flv",
        ".wmv",
    )
