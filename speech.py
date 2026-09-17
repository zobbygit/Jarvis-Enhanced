import queue
import threading
import logging
import pyttsx3
import speech_recognition as sr

logger = logging.getLogger(__name__)


class TTSEngine:
    """Async TTS — engine is created AND used inside the same worker thread."""

    def __init__(self, voice_index: int = 0, rate: int = 180):
        self.voice_index = voice_index
        self.rate = rate
        self._queue: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self._ready = threading.Event()      # signals engine is initialized

        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()
        # Wait until the engine is actually ready before returning
        self._ready.wait(timeout=10)

    def _loop(self):
        # ---- Create engine INSIDE this thread (critical!) ----
        try:
            engine = pyttsx3.init("sapi5")
        except Exception as e:
            logger.error("Failed to init TTS engine: %s", e)
            self._ready.set()
            return

        voices = engine.getProperty("voices")
        idx = self.voice_index if 0 <= self.voice_index < len(voices) else 0
        engine.setProperty("voice", voices[idx].id)
        engine.setProperty("rate", self.rate)
        self._ready.set()

        while not self._stop.is_set():
            try:
                text = self._queue.get(timeout=0.3)
            except queue.Empty:
                continue
            if text is None:
                continue
            try:
                engine.say(text)
                engine.runAndWait()
                engine.stop()          # helps SAPI5 on Windows stay stable
            except Exception as e:
                logger.error("TTS error: %s", e)

    def say(self, text: str):
        self._queue.put(text)

    def shutdown(self):
        self._stop.set()
        self._queue.put(None)


class SpeechRecognizer:
    def __init__(self, energy_threshold: int = 300, pause_threshold: float = 0.8):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.energy_threshold = energy_threshold

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        with sr.Microphone() as source:
            logger.info("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
                query = self.recognizer.recognize_google(audio, language="en-in")
                logger.info("User: %s", query)
                return query.lower()
            except sr.WaitTimeoutError:
                return "none"
            except sr.UnknownValueError:
                return "none"
            except Exception as e:
                logger.error("STT error: %s", e)
                return "none"