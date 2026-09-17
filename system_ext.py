import os
import subprocess
import logging

logger = logging.getLogger(__name__)


class SystemExtended:
    # ---------- Volume ----------
    @staticmethod
    def set_volume(percent: int):
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            iface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol = cast(iface, POINTER(IAudioEndpointVolume))
            vol.SetMasterVolumeLevelScalar(max(0, min(100, percent)) / 100, None)
            return True
        except Exception as e:
            logger.error("Volume error: %s", e)
            return False

    # ---------- Brightness ----------
    @staticmethod
    def set_brightness(percent: int):
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(max(0, min(100, percent)))
            return True
        except Exception as e:
            logger.error("Brightness error: %s", e)
            return False

    # ---------- Power ----------
    @staticmethod
    def lock_screen():
        os.system("rundll32.exe user32.dll,LockWorkStation")

    @staticmethod
    def shutdown(minutes: int = 0):
        os.system(f"shutdown /s /t {minutes * 60}")

    @staticmethod
    def restart(minutes: int = 0):
        os.system(f"shutdown /r /t {minutes * 60}")

    @staticmethod
    def cancel_shutdown():
        os.system("shutdown /a")

    # ---------- File search ----------
    @staticmethod
    def find_file(name: str, root: str = None, limit: int = 5):
        from thefuzz import fuzz
        root = root or os.path.expanduser("~")
        results = []
        for dirpath, _, files in os.walk(root):
            for f in files:
                score = fuzz.partial_ratio(name.lower(), f.lower())
                if score > 75:
                    results.append((score, os.path.join(dirpath, f)))
            if len(results) > 100:
                break
        results.sort(reverse=True)
        return [p for _, p in results[:limit]]

    # ---------- Process killer ----------
    @staticmethod
    def kill_process(name: str):
        try:
            import psutil
            killed = 0
            for p in psutil.process_iter(["name"]):
                if name.lower() in (p.info["name"] or "").lower():
                    try:
                        p.kill()
                        killed += 1
                    except Exception:
                        pass
            return killed
        except Exception as e:
            logger.error("Kill error: %s", e)
            return 0

    # ---------- Dictation ----------
    @staticmethod
    def type_text(text: str):
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=0.02)
            return True
        except Exception as e:
            logger.error("Type error: %s", e)
            return False