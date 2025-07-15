"""Generate concise, actionable meeting summaries."""
import base64
from typing import List
from openai import OpenAI
import os

class SummaryGenerator:
    """Uses GPT-4 to draft a structured summary."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    # ------------------------------------------------------------------
    def generate(self, transcript: str, images: List[str]) -> str:
        prompt = self._build_prompt(transcript, images)
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert note-taker. Create structured, bullet-point "
                        "summaries with action items and decisions."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    @staticmethod
    def _build_prompt(transcript: str, images: List[str]) -> str:
        image_txt = "\n".join(f"- {os.path.basename(img)}" for img in images) or "No images."
        return (
            f"Transcript:\n{transcript}\n\n"
            f"Scene Images:\n{image_txt}\n\n"
            "Please produce:\n"
            "• Executive summary\n"
            "• Action items (with owners if identifiable)\n"
            "• Key instructions or decisions"
        )
