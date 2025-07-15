"""Folder monitor using Watchdog."""
import os
import time
import threading
from pathlib import Path
from typing import Callable, Tuple

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class _Handler(FileSystemEventHandler):
    """Internal handler capturing newly created files."""

    def __init__(
        self,
        callback: Callable[[str], None],
        supported_ext: Tuple[str, ...],
    ):
        super().__init__()
        self.callback = callback
        self.supported_ext = supported_ext

    # ---------------------------------------------------------------------
    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return
        file_path = event.src_path
        if file_path.lower().endswith(self.supported_ext):
            if _wait_for_completion(file_path):
                self.callback(file_path)


def _wait_for_completion(path: str, stable_secs: int = 3, timeout: int = 120) -> bool:
    """Poll file size until unchanged for `stable_secs` seconds."""
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


class FolderMonitor:
    """Public wrapper that manages Watchdog observer threads."""

    def __init__(
        self,
        watch_path: str,
        callback: Callable[[str], None],
        supported_ext: Tuple[str, ...],
    ):
        self.watch_path = watch_path
        self.callback = callback
        self.supported_ext = supported_ext
        self._observer = Observer()
        self._observer.schedule(
            _Handler(callback, supported_ext), watch_path, recursive=False
        )

    # ---------------------------------------------------------------------
    def start_async(self) -> None:
        thread = threading.Thread(target=self._observer.start, daemon=True)
        thread.start()
