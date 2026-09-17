import re
import datetime
import webbrowser

from utils import safe_eval, setup_logger
from responses import capability_lines, get_chitchat_reply

logger = setup_logger(__name__)


class CommandRouter:
    """
    Routes voice commands via regex -> handler mapping.
    Adding a new command = adding one line to `self.routes`.
    """

    def __init__(self, assistant):
        self.a = assistant
        self.routes = [
            (r"\bwikipedia\b", self._wikipedia),
            (r"\bopen youtube\b", self._make_url("https://youtube.com", "YouTube")),
            (r"\bopen google\b", self._make_url("https://google.com", "Google")),
            (r"\bopen github\b", self._make_url("https://github.com", "GitHub")),
            (r"\bsearch google for\b", self._google_search),
            (r"\btime\b", self._time),
            (r"\bdate\b", self._date),
            (r"\bopen (vs code|code)\b", self._make_app("code", "Visual Studio Code")),
            (r"\bopen notepad\b", self._make_app("notepad", "Notepad")),
            (r"\bopen calculator\b", self._make_app("calc", "Calculator")),
            (r"\bplay music\b", self._music),
            (r"\bsend email\b", self._email),
            (r"\b(weather|temperature)\s+(in|at|for)\s+(?P<city>.+)", self._weather_direct),
            (r"\bwhat'?s the weather (in|at|for)\s+(?P<city>.+)", self._weather_direct),
            (r"\bweather\b", self._weather),
            (r"\bnews\b", self._news),
            (r"\b(system|battery)\b", self._system),
            (r"\b(screenshot|capture screen)\b", self._screenshot),
            (r"\bjoke\b", self._joke),
            (r"\b(calculate|compute)\b", self._calculate),
            (r"\badd contact\b", self._add_contact),
            (r"\b(remind me|set reminder)\b", self._reminder),
            (r"\b(exit|quit|bye)\b", lambda q, m: "exit"),
            (r"\b(sleep|stop listening)\b", lambda q, m: "sleep"),
            (
                r"\b(what can you do|what are your (capabilities|features)|"
                r"features|commands|what can i (ask|say)|help me out)\b",
                self._capabilities,
            ),
            (r"^\s*help\s*$", self._capabilities),

            # ---------- Vision ----------
            (r"\benroll (my )?face\b|\bsave (my )?face\b", self._enroll_face),
            (r"\bwho am i\b|\brecognize me\b", self._recognize),
            (r"\bread (what'?s on )?(the )?screen\b|\bocr\b", self._ocr_screen),
            (r"\bscan (a )?(qr|barcode)\b", self._scan_qr),
            (r"\bdetect motion\b|\bany motion\b", self._motion),

            # ---------- Telegram ----------
            (r"\bsend (a )?telegram\b", self._telegram_send),

            # ---------- Productivity ----------
            (
                r"\badd (a )?task\b|\badd to (my )?(to-?do|list)\b|\badd todo\b",
                self._add_todo,
            ),
            (
                r"\b(show|list|read) (my )?(to-?dos|tasks)\b|"
                r"\bwhat('?s| is) on my (list|to-?do)\b",
                self._list_todos,
            ),
            (r"\b(complete|finish|done) task\b", self._complete_todo),
            (r"\b(take a )?note\b|\bmake a note\b", self._add_note),
            (
                r"\b(start|begin) (a )?pomodoro\b|\bfocus (session|mode)\b",
                self._pomodoro,
            ),
            (r"\bi (drank|had) water\b|\blog water\b", self._log_water),
            (r"\b(set )?water reminder\b", self._water_reminder),
            (r"\bmorning briefing\b|\bdaily briefing\b|\bbrief me\b", self._briefing),
            (r"\bschedule briefing\b", self._schedule_briefing),

            # ---------- System extended ----------
            (
                r"\b(volume|sound) (to )?(\d+)\b|\bset volume\b",
                self._set_volume,
            ),
            (r"\b(mute|silence)\b", self._mute),
            (
                r"\bbrightness (to )?(\d+)\b|\bset brightness\b",
                self._set_brightness,
            ),
            (r"\block (the )?(screen|computer|pc)\b", self._lock),
            (r"\bshut ?down\b|\bshutdown\b", self._shutdown),
            (r"\brestart\b|\breboot\b", self._restart),
            (r"\bcancel shutdown\b", self._cancel_shutdown),
            (r"\bfind (the )?file\b|\bsearch (for )?file\b", self._find_file),
            (r"\b(kill|close|stop) (the )?(process|app)\b", self._kill_proc),
            (r"\bstart dictation\b|\btype what i say\b", self._dictation),

            # ---------- Personality ----------
            (r"\bmy name is\b|\bcall me\b", self._set_name),
            (r"\bwhat('?s| is) my name\b", self._get_name),
        ]
    def _weather_direct(self, q, m):
        city = m.group("city").strip().rstrip("?.!")
        r = self.a.weather.get(city)
        if "error" in r:
            self.a.speak(r["error"])
        else:
            self.a.speak(
                f"Temperature in {r['city']} is {r['temp']} degrees "
                f"celsius with {r['description']}"
                )
            return True
    # ---------- Vision ----------

    def _enroll_face(self, q, m):
        self.a.speak("What name should I save this face as?")
        name = self.a.listen()

        if name != "none":
            self.a.speak(self.a.vision.enroll_face(name))

        return True

    def _recognize(self, q, m):
        name = self.a.vision.recognize()
        self.a.speak(
            f"I see {name}." if name else "I don't recognize anyone."
        )
        return True

    def _ocr_screen(self, q, m):
        self.a.speak("Reading your screen...")
        self.a.speak(self.a.vision.read_screen()[:500])
        return True

    def _scan_qr(self, q, m):
        self.a.speak(self.a.vision.scan_qr())
        return True

    def _motion(self, q, m):
        self.a.speak("Watching for motion...")
        self.a.speak(self.a.vision.motion_check())
        return True

    # ---------- Telegram ----------

    def _telegram_send(self, q, m):
        self.a.speak("What should I send?")
        msg = self.a.listen()

        if msg != "none" and self.a.telegram:
            self.a.telegram.send(
                self.a.config.TELEGRAM_CHAT_ID,
                msg,
            )
            self.a.speak("Message sent.")

        return True

    # ---------- Productivity ----------

    def _add_todo(self, q, m):
        self.a.speak("What is the task?")
        task = self.a.listen()

        if task != "none":
            self.a.productivity.add_todo(task)

        return True

    def _list_todos(self, q, m):
        self.a.productivity.list_todos()
        return True

    def _complete_todo(self, q, m):
        self.a.speak("Which task number?")
        n = self.a.listen()

        try:
            self.a.productivity.complete_todo(
                int("".join(filter(str.isdigit, n)))
            )
        except Exception:
            self.a.speak("Invalid task number.")

        return True

    def _add_note(self, q, m):
        self.a.speak("What should I note down?")
        text = self.a.listen()

        if text != "none":
            self.a.productivity.add_note(text)

        return True

    def _pomodoro(self, q, m):
        self.a.speak("How many minutes?")
        n = self.a.listen()

        try:
            mins = int("".join(filter(str.isdigit, n))) or 25
            self.a.productivity.pomodoro(mins)
        except Exception:
            self.a.speak("Invalid duration.")

        return True

    def _log_water(self, q, m):
        self.a.productivity.log_habit("water")
        return True

    def _water_reminder(self, q, m):
        self.a.productivity.start_water_reminder(
            self.a.config.WATER_REMINDER_MINUTES
        )
        return True

    def _briefing(self, q, m):
        self.a.productivity.morning_briefing()
        return True

    def _schedule_briefing(self, q, m):
        self.a.productivity.schedule_briefing(
            self.a.config.BRIEFING_TIME
        )
        return True

    # ---------- System extended ----------

    def _set_volume(self, q, m):
        digits = "".join(filter(str.isdigit, q))

        if digits and self.a.system_ext.set_volume(int(digits)):
            self.a.speak(f"Volume set to {digits} percent.")

        return True

    def _mute(self, q, m):
        self.a.system_ext.set_volume(0)
        self.a.speak("Muted.")
        return True

    def _set_brightness(self, q, m):
        digits = "".join(filter(str.isdigit, q))

        if digits and self.a.system_ext.set_brightness(int(digits)):
            self.a.speak(f"Brightness set to {digits} percent.")

        return True

    def _lock(self, q, m):
        self.a.speak("Locking the screen.")
        self.a.system_ext.lock_screen()
        return True

    def _shutdown(self, q, m):
        self.a.speak(
            "Shutting down in 30 seconds. Say cancel shutdown to abort."
        )
        self.a.system_ext.shutdown(0.5)
        return True

    def _restart(self, q, m):
        self.a.speak("Restarting soon.")
        self.a.system_ext.restart(0.5)
        return True

    def _cancel_shutdown(self, q, m):
        self.a.system_ext.cancel_shutdown()
        self.a.speak("Shutdown cancelled.")
        return True

    def _find_file(self, q, m):
        self.a.speak("What filename should I search for?")
        name = self.a.listen()

        if name == "none":
            return True

        self.a.speak("Searching...")
        files = self.a.system_ext.find_file(name)

        if not files:
            self.a.speak("No matches found.")
        else:
            for f in files[:3]:
                self.a.speak(f)

        return True

    def _kill_proc(self, q, m):
        self.a.speak("Which application should I close?")
        name = self.a.listen()

        if name == "none":
            return True

        n = self.a.system_ext.kill_process(name)

        self.a.speak(
            f"Closed {n} process."
            if n
            else "No matching process found."
        )

        return True

    def _dictation(self, q, m):
        self.a.speak(
            "Dictation mode. Say 'stop dictation' to end."
        )

        while True:
            text = self.a.listen()

            if text == "none":
                continue

            if "stop dictation" in text:
                self.a.speak("Dictation stopped.")
                break

            self.a.system_ext.type_text(text + " ")

        return True

    # ---------- Personality ----------

    def _set_name(self, q, m):
        name = re.sub(r".*(my name is|call me)", "", q).strip()

        if not name:
            self.a.speak("What should I call you?")
            name = self.a.listen()

        if name and name != "none":
            saved = self.a.personality.set_name(name)
            self.a.speak(f"Nice to meet you, {saved}.")

        return True

    def _get_name(self, q, m):
        self.a.speak(
            f"Your name is {self.a.personality.get_name()}."
        )
        return True

    # ---------- Dispatch ----------

    def dispatch(self, query: str):
        # 1. Try explicit command routes first
        for pattern, handler in self.routes:
            m = re.search(pattern, query)

            if m:
                return handler(query, m)
            mood_reply = self.a.personality.detect_mood(query)
            if mood_reply:
                self.a.speak(mood_reply)
                return True

        # 2. Try general chit-chat
        reply = get_chitchat_reply(query)

        if reply:
            self.a.speak(reply)
            return True

        # 3. Nothing matched
        self.a.speak(
            "I didn't understand that command. Please try again."
        )
        return True

    # ---------- General Commands ----------

    def _capabilities(self, query, match=None):
        for line in capability_lines():
            self.a.speak(line)

        return True

    # ---------- Helper factories ----------

    def _make_url(self, url, name):
        def _h(q, m):
            self.a.speak(f"Opening {name}")
            webbrowser.open(url)
            return True

        return _h

    def _make_app(self, cmd, name):
        def _h(q, m):
            self.a.speak(f"Opening {name}")
            self.a.system.open_app(cmd)
            return True

        return _h

    # ---------- Handlers ----------

    def _wikipedia(self, query, m):
        self.a.speak("Searching Wikipedia...")
        term = query.replace("wikipedia", "").strip()
        result = self.a.wiki.search(term)

        if isinstance(result, dict):
            if "disambiguation" in result:
                self.a.speak(
                    "Ambiguous. Did you mean: "
                    + ", ".join(result["disambiguation"])
                )
            else:
                self.a.speak(
                    result.get("error", "Not found")
                )
        else:
            self.a.speak("According to Wikipedia")
            self.a.speak(result)

        return True

    def _google_search(self, query, m):
        term = query.replace("search google for", "").strip()
        self.a.speak(f"Searching Google for {term}")
        webbrowser.open(
            f"https://www.google.com/search?q={term}"
        )
        return True

    def _time(self, q, m):
        self.a.speak(
            f"The time is "
            f"{datetime.datetime.now().strftime('%H:%M:%S')}"
        )
        return True

    def _date(self, q, m):
        self.a.speak(
            f"Today's date is "
            f"{datetime.datetime.now().strftime('%B %d, %Y')}"
        )
        return True

    def _music(self, q, m):
        self.a.speak("Playing music")
        song = self.a.system.play_music(
            self.a.config.MUSIC_DIR
        )

        if not song:
            self.a.speak("No music files found")

        return True

    def _email(self, q, m):
        try:
            self.a.speak("To whom should I send the email?")
            recipient = self.a.listen()
            to_email = self.a.contacts.get(recipient)

            if not to_email:
                self.a.speak(
                    "Contact not found. Please provide email address"
                )
                to_email = self.a.listen()

            self.a.speak("What is the subject?")
            subject = self.a.listen()

            self.a.speak("What should I say?")
            body = self.a.listen()

            if self.a.email.send(to_email, subject, body):
                self.a.speak("Email sent successfully!")
            else:
                self.a.speak(
                    "Sorry, I couldn't send the email."
                )

        except Exception as e:
            logger.error("Email flow error: %s", e)
            self.a.speak("Unable to send email")

        return True

    def _weather(self, q, m):
        self.a.speak("Which city?")
        city = self.a.listen()

        if city == "none":
            return True

        r = self.a.weather.get(city)

        if "error" in r:
            self.a.speak(r["error"])
        else:
            self.a.speak(
                f"Temperature in {r['city']} is "
                f"{r['temp']} degrees celsius "
                f"with {r['description']}"
            )

        return True

    def _news(self, q, m):
        headlines = self.a.news.get_top()

        if isinstance(headlines, dict):
            self.a.speak(
                headlines.get("error", "News unavailable")
            )
        else:
            self.a.speak("Here are the top headlines:")

            for i, h in enumerate(headlines, 1):
                self.a.speak(f"Headline {i}: {h}")

        return True

    def _system(self, q, m):
        info = self.a.system.system_info()

        self.a.speak(
            f"CPU usage is {info['cpu']} percent"
        )
        self.a.speak(
            f"Memory usage is {info['memory']} percent"
        )

        if info["battery"]:
            self.a.speak(
                f"Battery is at "
                f"{info['battery'].percent} percent"
            )

            if info["battery"].power_plugged:
                self.a.speak("Charger is plugged in")

        return True

    def _screenshot(self, q, m):
        f = self.a.system.screenshot()

        self.a.speak(
            "Screenshot saved"
            if f
            else "Unable to take screenshot"
        )

        return True

    def _joke(self, q, m):
        self.a.speak(self.a.system.joke())
        return True

    def _calculate(self, q, m):
        expr = (
            q.replace("calculate", "")
            .replace("compute", "")
            .strip()
        )

        try:
            self.a.speak(
                f"The result is {safe_eval(expr)}"
            )
        except Exception as e:
            logger.warning("Calc failed: %s", e)
            self.a.speak("Unable to calculate")

        return True

    def _add_contact(self, q, m):
        self.a.speak("What is the name?")
        name = self.a.listen()

        self.a.speak("What is the email?")
        email = self.a.listen()

        if name != "none" and email != "none":
            self.a.contacts[name.lower()] = email
            self.a.save_contacts()
            self.a.speak(
                f"Contact {name} added successfully"
            )

        return True

    def _reminder(self, q, m):
        self.a.speak("What should I remind you about?")
        text = self.a.listen()

        self.a.speak("In how many minutes?")
        mins = self.a.listen()

        try:
            self.a.set_reminder(
                text,
                int("".join(filter(str.isdigit, mins))),
            )
        except Exception:
            self.a.speak("Invalid time format")

        return True