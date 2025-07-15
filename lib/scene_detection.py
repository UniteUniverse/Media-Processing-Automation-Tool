"""Scene change detection and key-frame extraction."""
import os
from typing import List, Tuple
import cv2
from scenedetect import detect, AdaptiveDetector


class SceneDetector:
    """High-level scene change utility."""

    def detect_and_extract(
        self, video_path: str, output_dir: str
    ) -> Tuple[List[Tuple[str, str]], List[str]]:
        """Return (scene timecodes, keyframe image paths)."""
        scenes = detect(video_path, AdaptiveDetector())
        keyframes = []
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        for idx, (start, end) in enumerate(scenes):
            mid_time = (start.get_seconds() + end.get_seconds()) / 2
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(mid_time * fps))
            ret, frame = cap.read()
            if not ret:
                continue
            img_path = os.path.join(output_dir, f"{os.path.basename(video_path)}_scene_{idx:03d}.jpg")
            cv2.imwrite(img_path, frame)
            keyframes.append(img_path)

        cap.release()
        return [(s[0].get_timecode(), s[1].get_timecode()) for s in scenes], keyframes
