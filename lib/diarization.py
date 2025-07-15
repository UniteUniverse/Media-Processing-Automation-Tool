"""Speaker diarization with pyannote.audio."""
from pathlib import Path
from typing import Optional
from pyannote.audio import Pipeline


class DiarizationService:
    """Encapsulates Hugging Face diarization pipeline."""

    def __init__(self, auth_token: str):
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1", use_auth_token=auth_token
        )

    # ------------------------------------------------------------------
    def diarize(
        self,
        wav_path: str,
        num_speakers: Optional[int],
        output_dir: str,
    ) -> str:
        diarization = (
            self.pipeline(wav_path, num_speakers=num_speakers)
            if num_speakers
            else self.pipeline(wav_path)
        )
        out_file = Path(output_dir) / (Path(wav_path).stem + ".rttm")
        with open(out_file, "w", encoding="utf-8") as fp:
            diarization.write_rttm(fp)
        return out_file.as_posix()
