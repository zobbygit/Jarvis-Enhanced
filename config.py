import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    WEATHER_API   = os.getenv("WEATHER_API")
    NEWS_API      = os.getenv("NEWS_API")
    EMAIL_USER    = os.getenv("EMAIL_USER")
    EMAIL_PASS    = os.getenv("EMAIL_PASS")
    DEFAULT_CITY  = os.getenv("DEFAULT_CITY", "Kolkata")
    MUSIC_DIR     = os.getenv("MUSIC_DIR", "")
    VOICE_INDEX   = int(os.getenv("VOICE_INDEX", "0"))
    SPEECH_RATE   = int(os.getenv("SPEECH_RATE", "180"))
    LOG_LEVEL     = os.getenv("LOG_LEVEL", "INFO")
    USE_WAKE_WORD = os.getenv("USE_WAKE_WORD", "false").lower() == "true"
    WAKE_WORD     = os.getenv("WAKE_WORD", "jarvis")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    FACES_DIR = os.getenv("FACES_DIR", "known_faces")
    USER_NAME = os.getenv("USER_NAME", "")
    BRIEFING_TIME = os.getenv("BRIEFING_TIME", "08:00")
    WATER_REMINDER_MINUTES = int(os.getenv("WATER_REMINDER_MINUTES", "60"))

    _REQUIRED = ["WEATHER_API", "NEWS_API", "EMAIL_USER", "EMAIL_PASS"]

    @classmethod
    def validate(cls):
        missing = [k for k in cls._REQUIRED if not getattr(cls, k)]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )