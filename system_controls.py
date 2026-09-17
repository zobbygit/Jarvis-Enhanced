import os
import random
import datetime
import psutil
import pyautogui
import pyjokes
from utils import setup_logger

logger = setup_logger(__name__)


class SystemController:
    def system_info(self) -> dict:
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "battery": psutil.sensors_battery(),
        }

    def screenshot(self, directory: str = ".") -> str | None:
        try:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(directory, f"screenshot_{ts}.png")
            pyautogui.screenshot().save(path)
            return path
        except Exception as e:
            logger.error("Screenshot error: %s", e)
            return None

    @staticmethod
    def open_app(command: str) -> bool:
        try:
            os.system(command)
            return True
        except Exception as e:
            logger.error("Open app error: %s", e)
            return False

    @staticmethod
    def play_music(music_dir: str) -> str | None:
        if not music_dir or not os.path.isdir(music_dir):
            return None
        songs = [s for s in os.listdir(music_dir)
                 if s.lower().endswith((".mp3", ".wav", ".m4a"))]
        if not songs:
            return None
        song = random.choice(songs)
        os.startfile(os.path.join(music_dir, song))
        return song

    @staticmethod
    def joke() -> str:
        return pyjokes.get_joke()