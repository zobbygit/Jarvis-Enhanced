import os
import json
import random
import datetime
import logging

logger = logging.getLogger(__name__)

USER_FILE = "user.json"


class Personality:
    def __init__(self, default_name: str = "Sir"):
        self.default_name = default_name
        self.data = self._load()

    def _load(self):
        try:
            with open(USER_FILE) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save(self):
        with open(USER_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    # ---------- Name memory ----------
    def set_name(self, name):
        self.data["name"] = name.strip().title()
        self._save()
        return self.data["name"]

    def get_name(self):
        return self.data.get("name", self.default_name)

    def has_name(self):
        return "name" in self.data

    # ---------- Time-aware greeting ----------
    def greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            base = "Good morning"
        elif hour < 18:
            base = "Good afternoon"
        else:
            base = "Good evening"
        name = self.get_name()
        return f"{base}, {name}!" if name != self.default_name else f"{base}!"

    # ---------- Mood detection ----------
    MOODS = {
        "tired":    ["You sound tired. Want a short break or some music?"],
        "stressed": ["Take a deep breath. I can help you organize tasks."],
        "happy":    ["Love the energy! What would you like to do?"],
        "sad":      ["I'm here for you. Want a joke to lighten things up?"],
        "bored":    ["Let's fix that — want a joke, a fun fact, or some music?"],
    }

    def detect_mood(self, text):
        t = text.lower()
        for mood, replies in self.MOODS.items():
            if mood in t or f"i am {mood}" in t or f"i'm {mood}" in t:
                return random.choice(replies)
        return None