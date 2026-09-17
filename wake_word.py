import os
import json
import logging

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Passive listener — only triggers when the wake word is spoken."""
    def __init__(self, wake_word: str = "jarvis", model_path: str | None = None):
        try:
            from vosk import Model, KaldiRecognizer
            import pyaudio
        except ImportError as e:
            raise ImportError("Install 'vosk' and 'pyaudio' for wake word") from e

        model_path = model_path or "vosk-model-small-en-us-0.15"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at {model_path}")

        self.wake_word = wake_word.lower()
        self.rec = KaldiRecognizer(Model(model_path), 16000)
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16, channels=1, rate=16000,
            input=True, frames_per_buffer=8000,
        )
        self.stream.start_stream()

    def wait(self) -> bool:
        logger.info("Waiting for wake word '%s'...", self.wake_word)
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                if self.wake_word in json.loads(self.rec.Result()).get("text", "").lower():
                    logger.info("Wake word detected!")
                    return True

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()