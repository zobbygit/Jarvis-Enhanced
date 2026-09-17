import os
import json
import time
import threading
import datetime
import logging

logger = logging.getLogger(__name__)

TODO_FILE = "todos.json"
NOTES_FILE = "notes.md"
HABITS_FILE = "habits.json"


class Productivity:
    def __init__(self, speak_cb, weather_cb, news_cb):
        self.speak = speak_cb
        self.get_weather = weather_cb
        self.get_news = news_cb
        self._ensure_files()

    def _ensure_files(self):
        for f, default in [(TODO_FILE, []), (HABITS_FILE, {})]:
            if not os.path.exists(f):
                with open(f, "w") as fp:
                    json.dump(default, fp)

    # ---------- To-Do ----------
    def _load_todos(self):
        with open(TODO_FILE) as f:
            return json.load(f)

    def _save_todos(self, data):
        with open(TODO_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def add_todo(self, text):
        todos = self._load_todos()
        todos.append({"task": text, "done": False,
                      "created": datetime.datetime.now().isoformat()})
        self._save_todos(todos)
        self.speak(f"Added '{text}' to your to-do list.")

    def list_todos(self):
        todos = [t for t in self._load_todos() if not t["done"]]
        if not todos:
            self.speak("Your to-do list is empty.")
            return
        self.speak(f"You have {len(todos)} pending tasks.")
        for i, t in enumerate(todos, 1):
            self.speak(f"{i}. {t['task']}")

    def complete_todo(self, num):
        todos = self._load_todos()
        pending = [t for t in todos if not t["done"]]
        if 1 <= num <= len(pending):
            pending[num - 1]["done"] = True
            self._save_todos(todos)
            self.speak(f"Marked '{pending[num-1]['task']}' as done.")

    # ---------- Notes ----------
    def add_note(self, text):
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n## {datetime.datetime.now():%Y-%m-%d %H:%M}\n{text}\n")
        self.speak("Note saved.")

    # ---------- Pomodoro ----------
    def pomodoro(self, minutes=25):
        def worker():
            time.sleep(minutes * 60)
            self.speak("Focus session complete. Time for a break!")
        threading.Thread(target=worker, daemon=True).start()
        self.speak(f"Pomodoro started for {minutes} minutes.")

    # ---------- Habits ----------
    def log_habit(self, habit):
        with open(HABITS_FILE) as f:
            data = json.load(f)
        today = datetime.date.today().isoformat()
        data.setdefault(habit, {})
        data[habit][today] = data[habit].get(today, 0) + 1
        with open(HABITS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        self.speak(f"Logged {habit} for today.")

    # ---------- Water reminder (background) ----------
    def start_water_reminder(self, minutes=60):
        def loop():
            while True:
                time.sleep(minutes * 60)
                self.speak("Time to drink some water.")
        threading.Thread(target=loop, daemon=True).start()
        self.speak(f"Water reminder set every {minutes} minutes.")

    # ---------- Morning briefing ----------
    def morning_briefing(self):
        self.speak("Good morning. Here is your briefing.")
        try:
            self.get_weather(None)
        except Exception:
            pass
        try:
            self.get_news()
        except Exception:
            pass
        todos = [t for t in self._load_todos() if not t["done"]]
        if todos:
            self.speak(f"You have {len(todos)} tasks on your list today.")

    def schedule_briefing(self, hhmm):
        try:
            import schedule
        except ImportError:
            logger.error("pip install schedule")
            return
        schedule.every().day.at(hhmm).do(self.morning_briefing)

        def runner():
            while True:
                schedule.run_pending()
                time.sleep(30)
        threading.Thread(target=runner, daemon=True).start()
        self.speak(f"Morning briefing scheduled at {hhmm}.")