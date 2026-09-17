import datetime
import json
import threading

from config import Config
from utils import setup_logger
from speech import TTSEngine, SpeechRecognizer
from api_services import WeatherService, NewsService, WikiService
from email_service import EmailService
from system_controls import SystemController
from router import CommandRouter
from vision import VisionService
from telegram_bot import TelegramRemote
from productivity import Productivity
from system_ext import SystemExtended
from personality import Personality


logger = setup_logger(__name__, level=Config.LOG_LEVEL)


class VoiceAssistant:
    def __init__(self):
        Config.validate()
        self.config = Config

        # ---------- Services ----------
        self.tts = TTSEngine(
            Config.VOICE_INDEX,
            Config.SPEECH_RATE,
        )
        self.stt = SpeechRecognizer()
        self.weather = WeatherService(Config.WEATHER_API)
        self.news = NewsService(Config.NEWS_API)
        self.wiki = WikiService()
        self.system = SystemController()
        self.email = EmailService(
            Config.EMAIL_USER,
            Config.EMAIL_PASS,
        )

        # ---------- State ----------
        self.assistant_name = "Jarvis"
        self.contacts = self._load_contacts()
        self.conversation_history = []
        self.sleep_mode = False

        # ---------- Vision ----------
        self.vision = VisionService(
            faces_dir=Config.FACES_DIR
        )

        # ---------- Extended system ----------
        self.system_ext = SystemExtended()

        # ---------- Personality ----------
        self.personality = Personality(
            default_name="Sir"
        )

        # ---------- Remote speaker buffer ----------
        self._remote_buffer = None

        # ---------- Productivity ----------
        self.productivity = Productivity(
            speak_cb=self.speak,
            weather_cb=lambda _: self._speak_weather(),
            news_cb=lambda: self._speak_news(),
        )

        # ---------- Telegram remote ----------
        self.telegram = None

        if Config.TELEGRAM_TOKEN:
            self.telegram = TelegramRemote(
                Config.TELEGRAM_TOKEN,
                Config.TELEGRAM_CHAT_ID,
            )
            self.telegram.on_message = (
                self._handle_remote_command
            )
            self.telegram.start()

        # ---------- Optional wake-word ----------
        self.wake = None

        if Config.USE_WAKE_WORD:
            try:
                from wake_word import WakeWordDetector

                self.wake = WakeWordDetector(
                    Config.WAKE_WORD
                )

            except Exception as e:
                logger.warning(
                    "Wake word unavailable, falling back: %s",
                    e,
                )

        # ---------- Router ----------
        self.router = CommandRouter(self)

    # ---------- I/O ----------

    def speak(self, text: str):
        logger.info(
            "%s: %s",
            self.assistant_name,
            text,
        )

        if self._remote_buffer is not None:
            self._remote_buffer.append(text)
        else:
            self.tts.say(text)

    def listen(self) -> str:
        query = self.stt.listen()

        if query != "none":
            self.conversation_history.append(
                {
                    "user": query,
                    "time": datetime.datetime.now().isoformat(),
                }
            )

        return query

    # ---------- Contacts ----------

    def _load_contacts(self) -> dict:
        try:
            with open("contacts.json", "r") as f:
                return json.load(f)

        except FileNotFoundError:
            return {
                "example": "example@gmail.com"
            }

        except json.JSONDecodeError as e:
            logger.error(
                "Corrupted contacts file: %s",
                e,
            )
            return {}

    def save_contacts(self):
        with open("contacts.json", "w") as f:
            json.dump(
                self.contacts,
                f,
                indent=4,
            )

    # ---------- Reminders ----------

    def set_reminder(
        self,
        text: str,
        minutes: int,
    ):
        def worker():
            import time

            time.sleep(minutes * 60)
            self.speak(f"Reminder: {text}")

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

        self.speak(
            f"Reminder set for {minutes} minutes"
        )

    # ---------- Greeting ----------

    def wish_me(self):
        greeting = self.personality.greeting()
        self.speak(f"{greeting} I am {self.assistant_name}, your assistant. "
                   f"How can I help you today?")

        # First run — ask for name
        if not self.personality.has_name() and not Config.USER_NAME:
            self.speak("By the way, what should I call you?")
            name = self.listen()
            if name and name != "none":
                self.personality.set_name(name)
                self.speak(
                    f"Got it. I'll remember that, "
                    f"{self.personality.get_name()}."
                )

    # ---------- Weather / News helpers ----------

    def _speak_weather(self):
        r = self.weather.get(self.config.DEFAULT_CITY)
        if "error" in r:
            self.speak(r["error"])
        else:
            self.speak(
                f"Temperature in {r['city']} is {r['temp']} degrees "
                f"celsius with {r['description']}"
            )

    def _speak_news(self):
        headlines = self.news.get_top()
        if isinstance(headlines, dict):
            self.speak(headlines.get("error", "News unavailable"))
        else:
            self.speak("Here are the top headlines:")
            for i, h in enumerate(headlines, 1):
                self.speak(f"Headline {i}: {h}")

    # ---------- Telegram handler ----------

    def _handle_remote_command(self, text: str, chat_id: str):
        """Telegram messages go through the same router, replies routed back."""
        logger.info("Telegram: %s", text)
        self._remote_buffer = []
        try:
            self.router.dispatch(text)
        except Exception as e:
            self._remote_buffer.append(f"Error: {e}")

        reply = "\n".join(self._remote_buffer) or "Done."
        self._remote_buffer = None

        if self.telegram:
            self.telegram.send(chat_id, reply)

    # ---------- Main loop ----------

    def run(self):
        self.wish_me()

        try:
            while True:
                # Optional: passive wake-word gate
                if self.wake and self.sleep_mode:
                    self.wake.wait()
                    self.sleep_mode = False
                    self.speak("I'm back online!")

                query = self.listen()

                if query == "none":
                    continue

                if self.sleep_mode:
                    if (
                        "wake up" in query
                        or Config.WAKE_WORD in query
                    ):
                        self.sleep_mode = False
                        self.speak("I'm back online!")

                    continue

                result = self.router.dispatch(query)

                if result == "sleep":
                    self.sleep_mode = True

                elif result == "exit":
                    self.speak(
                        "Goodbye! Have a great day!"
                    )
                    break

        except KeyboardInterrupt:
            self.speak("Shutting down")

        finally:
            self.tts.shutdown()

            if self.wake:
                self.wake.close()


if __name__ == "__main__":
    VoiceAssistant().run()