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

    def _load(self):
        try:
            with open(self.enc_file, "rb") as f:
                d = pickle.load(f)
                self.encodings, self.names = d["encodings"], d["names"]
        except FileNotFoundError:
            pass

    def _save(self):
        with open(self.enc_file, "wb") as f:
            pickle.dump({"encodings": self.encodings, "names": self.names}, f)

    def _grab(self):
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()
        return frame if ret else None

    def enroll_face(self, name: str) -> str:
        try:
            import face_recognition
        except ImportError:
            return "face_recognition not installed"
        frame = self._grab()
        if frame is None:
            return "Camera unavailable"
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)
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
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        for enc in face_recognition.face_encodings(rgb):
            matches = face_recognition.compare_faces(self.encodings, enc, tolerance=0.5)
            if True in matches:
                return self.names[matches.index(True)]
        return None

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
        ret, prev = cam.read()
        if not ret:
            cam.release()
            return "Camera unavailable"
        prev = cv2.GaussianBlur(cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY), (21, 21), 0)
        start = time.time()
        while time.time() - start < seconds:
            ret, frame = cam.read()
            if not ret:
                break
            gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
            delta = cv2.absdiff(prev, gray)
            if cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1].sum() > 500000:
                cam.release()
                return "Motion detected"
            prev = gray
        cam.release()
        return "No motion detected"