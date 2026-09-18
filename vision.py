import os
import cv2
import time
import pickle
import logging
import numpy as np

logger = logging.getLogger(__name__)


class VisionService:
    def __init__(self, faces_dir="known_faces", enc_file="face_encodings.pkl"):
        self.faces_dir = faces_dir
        self.enc_file = enc_file
        self.encodings = []
        self.names = []
        os.makedirs(faces_dir, exist_ok=True)
        self._load()

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def _load(self):
        try:
            with open(self.enc_file, "rb") as f:
                d = pickle.load(f)
                self.encodings, self.names = d["encodings"], d["names"]
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.warning("Could not load face encodings: %s", e)

    def _save(self):
        with open(self.enc_file, "wb") as f:
            pickle.dump({"encodings": self.encodings, "names": self.names}, f)

    # ------------------------------------------------------------------ #
    # Camera helpers
    # ------------------------------------------------------------------ #
    def _grab(self, warmup_frames: int = 5):
        """Open camera, discard a few frames so auto-exposure settles, then read one."""
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            cam.release()
            return None
        frame = None
        for _ in range(max(1, warmup_frames)):
            ret, f = cam.read()
            if ret:
                frame = f
        cam.release()
        return frame

    @staticmethod
    def _to_rgb_uint8(img):
        """Force any camera frame into a valid 8-bit RGB numpy array.

        face_recognition / dlib require:
          * dtype == uint8
          * 1 channel (gray) or 3 channels in RGB order
        OpenCV normally returns BGR uint8, but some backends (MSMF/DSHOW)
        can return float32, 4-channel, or grayscale frames.
        """
        if img is None:
            return None
        if not isinstance(img, np.ndarray):
            img = np.array(img)

        # 1) dtype -> uint8
        if img.dtype != np.uint8:
            if img.dtype.kind == "f":
                # float image: normalize 0..1 -> 0..255, otherwise clip
                if img.max() <= 1.0:
                    img = (img * 255.0).clip(0, 255).astype(np.uint8)
                else:
                    img = img.clip(0, 255).astype(np.uint8)
            else:
                img = img.astype(np.uint8)

        # 2) channels -> 3-channel RGB
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.ndim == 3:
            c = img.shape[2]
            if c == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            elif c == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif c == 1:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            else:
                raise ValueError(f"Unsupported channel count: {c}")
        else:
            raise ValueError(f"Unsupported image shape: {img.shape}")

        return np.ascontiguousarray(img, dtype=np.uint8)

    # ------------------------------------------------------------------ #
    # Face enrollment / recognition
    # ------------------------------------------------------------------ #
    def enroll_face(self, name: str) -> str:
        try:
            import face_recognition
        except ImportError:
            return "face_recognition not installed"

        frame = self._grab()
        if frame is None:
            return "Camera unavailable"

        try:
            rgb = self._to_rgb_uint8(frame)
        except Exception as e:
            logger.exception("Image conversion failed")
            return f"Image conversion error: {e}"

        try:
            encs = face_recognition.face_encodings(rgb)
        except Exception as e:
            logger.exception("face_encodings failed")
            return f"Face encoding error: {e}"

        if not encs:
            return "No face detected"

        self.encodings.append(encs[0])
        self.names.append(name.lower())
        self._save()
        return f"Face saved for {name}"

    def recognize(self):
        try:
            import face_recognition
        except ImportError:
            return None
        if not self.encodings:
            return None

        frame = self._grab()
        if frame is None:
            return None

        try:
            rgb = self._to_rgb_uint8(frame)
        except Exception:
            logger.exception("Image conversion failed")
            return None

        try:
            unknown = face_recognition.face_encodings(rgb)
        except Exception:
            logger.exception("face_encodings failed")
            return None

        for enc in unknown:
            matches = face_recognition.compare_faces(
                self.encodings, enc, tolerance=0.5
            )
            if True in matches:
                return self.names[matches.index(True)]
        return None

    # ------------------------------------------------------------------ #
    # Other utilities
    # ------------------------------------------------------------------ #
    def read_screen(self) -> str:
        try:
            import pyautogui
            import pytesseract
        except ImportError:
            return "pytesseract / pyautogui missing"
        img = pyautogui.screenshot()
        return pytesseract.image_to_string(img).strip() or "No text found"

    def scan_qr(self) -> str:
        try:
            from pyzbar import pyzbar
        except ImportError:
            return "pyzbar not installed"

        frame = self._grab()
        if frame is None:
            return "Camera unavailable"

        codes = pyzbar.decode(frame)
        return codes[0].data.decode("utf-8") if codes else "No QR code found"

    def motion_check(self, seconds: int = 5) -> str:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            cam.release()
            return "Camera unavailable"

        ret, prev = cam.read()
        if not ret:
            cam.release()
            return "Camera unavailable"

        prev = cv2.GaussianBlur(
            cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY), (21, 21), 0
        )
        start = time.time()
        try:
            while time.time() - start < seconds:
                ret, frame = cam.read()
                if not ret:
                    break
                gray = cv2.GaussianBlur(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0
                )
                delta = cv2.absdiff(prev, gray)
                thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
                if thresh.sum() > 500000:
                    return "Motion detected"
                prev = gray
        finally:
            cam.release()
        return "No motion detected"