"""OpenAI Whisper transcription service."""
from pathlib import Path
from typing import Dict, Any
from openai import OpenAI


class TranscriptionService:
    """Handles calls to OpenAI's speech-to-text."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def transcribe(self, audio_path: str, language: str = "auto") -> Dict[str, Any]:
        """Transcribe audio and return a dictionary-like structure."""
        with open(audio_path, "rb") as fp:
            resp = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=fp,
                response_format="verbose_json",
                timestamp_granularities=["word"],
                language=None if language == "auto" else language,
            )
        
        # Convert the response to a proper dictionary
        if hasattr(resp, 'model_dump'):
            # For Pydantic v2
            transcript_dict = resp.model_dump()
        elif hasattr(resp, 'dict'):
            # For Pydantic v1
            transcript_dict = resp.dict()
        else:
            # Fallback manual conversion
            transcript_dict = {
                "text": resp.text,
                "language": getattr(resp, 'language', 'unknown'),
                "duration": getattr(resp, 'duration', 0),
                "segments": getattr(resp, 'segments', []),
                "words": getattr(resp, 'words', [])
            }
        
        # Persist JSON next to audio
        json_path = Path(audio_path).with_suffix(".json")
        json_path.write_text(str(transcript_dict), encoding="utf-8")
        
        return transcript_dict

