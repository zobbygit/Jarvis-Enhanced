<div align="center">

# 🤖 Jarvis — Voice Assistant

**A free, offline-capable, extensible voice assistant built in pure Python.**

*No paid APIs. No cloud lock-in. Runs on your machine.*

[![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey?logo=windows)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

</div>

---

## 📖 Table of Contents

- [Features](#-features)
- [Demo Commands](#-demo-commands)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Telegram Remote](#-telegram-remote)
- [Wake Word Setup](#-wake-word-setup)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Privacy](#-privacy)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🎙️ Voice & Speech
- Wake-word activation (Vosk, fully offline)
- Text-to-speech via Windows SAPI5 (async, non-blocking)
- Speech recognition (Google STT or Vosk offline)
- Multi-language support (English-IN by default)

### 🌐 Information
- 🌤️ Live weather for any city (OpenWeatherMap, free tier)
- 📰 Top news headlines (NewsAPI, free tier)
- 📚 Wikipedia summaries with disambiguation handling
- 🔍 DuckDuckGo / Google search

### 📅 Productivity
- ✅ To-do list (`todos.json`)
- 📝 Quick notes (`notes.md` with timestamps)
- ⏱️ Pomodoro focus timer
- 💧 Water / posture reminders
- 🌅 Morning briefing (auto at `BRIEFING_TIME`)
- ⏰ Custom reminders (say it, done)

### 🖥️ System Control
- 🔊 Volume control (0–100%)
- ☀️ Screen brightness control
- 🔒 Lock / shutdown / restart / cancel shutdown
- 🔍 Fuzzy file search across your home folder
- 🗂️ Kill processes by name
- ⌨️ Dictation mode — speaks into any app

### 👁️ Vision (Offline)
- 😀 Face recognition — Jarvis greets *you* by name
- 📄 OCR — read text on your screen aloud
- 📷 QR / barcode scanning via webcam
- 👀 Motion detection

### 📱 Remote Access
- Telegram bot — control Jarvis from your phone anywhere
- Two-way messaging (send commands, receive replies)

### 🎭 Personality
- Remembers your name on first run
- Time-aware greetings (morning / afternoon / evening)
- Mood detection ("I'm tired" → offers a break)
- 40+ chit-chat categories, 90+ reply strings
- Capability list ("what can you do?")

### 🔒 Security & Privacy
- 100% local processing (except Telegram, optional)
- All secrets in `.env` (never committed)
- Encrypted-ready contacts storage
- No telemetry, no tracking

---

## 🎬 Demo Commands

> Say **"Jarvis"** (or your custom wake word), then:

| Category | Example |
|---|---|
| **Info** | `what's the weather in Kolkata` |
| | `tell me the news` |
| | `search Wikipedia for black holes` |
| **System** | `set volume to 40` |
| | `brightness 70` |
| | `lock the screen` |
| | `shut down in 10 minutes` |
| **Productivity** | `add buy milk to my list` |
| | `show my to-dos` |
| | `start a pomodoro` |
| | `take a note: meeting at 5pm` |
| **Vision** | `enroll my face` |
| | `who am I` |
| | `read what's on the screen` |
| | `scan a QR code` |
| **Personality** | `my name is Rahul` |
| | `how are you` |
| | `what can you do` |
| | `tell me a joke` |
| **Control** | `sleep` / `wake up` |
| | `goodbye` / `exit` |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       main.py (Orchestrator)                │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │  TTSEngine   │   │SpeechRecogn. │   │  VoiceAssistant│  │
│  │  (threaded)  │◄──┤   (mic)      │──►│     (core)     │  │
│  └──────────────┘   └──────────────┘   └───────┬────────┘  │
└──────────────────────────────────────────────┬─┴───────────┘
                                               │
                                    ┌──────────▼──────────┐
                                    │   CommandRouter     │
                                    │  (regex dispatch)   │
                                    └──────────┬──────────┘
                                               │
     ┌────────────┬────────────┬───────────────┼──────────────┬──────────────┐
     ▼            ▼            ▼               ▼              ▼              ▼
┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐ ┌───────────┐ ┌────────────┐
│ Weather │ │  News   │ │  Email   │ │  SystemCtrl  │ │  Vision   │ │Productivity│
│ Service │ │ Service │ │ Service  │ │ + SystemExt  │ │  Service  │ │  (local)   │
└─────────┘ └─────────┘ └──────────┘ └──────────────┘ └───────────┘ └────────────┘
                                               │
                                      ┌────────┴────────┐
                                      ▼                 ▼
                              ┌──────────────┐  ┌──────────────┐
                              │  Telegram    │  │ Personality  │
                              │   Remote     │  │  (memory)    │
                              └──────────────┘  └──────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Windows 10/11** (uses SAPI5 for TTS)
- **Microphone** + **Webcam** (for voice & vision features)
- *(Optional)* [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) for screen reading

### 1. Clone

```bash
git clone https://github.com/zobbygit/Jarvis-Enhanced
cd jarvis-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Windows note:** If `pyaudio` fails to install:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### 3. Create your `.env`

Copy the template and fill in your keys:

```bash
copy .env.example .env    # Windows
cp .env.example .env      # macOS / Linux
```

Then edit `.env` with your values (see [Configuration](#-configuration)).

### 4. Run

```bash
python main.py
```

You should hear: *"Good morning! I am Jarvis, your assistant. How can I help you today?"*

---

## ⚙️ Configuration

All configuration lives in `.env`. Here's what each key does:

| Variable | Required | Description | Get it free at |
|---|---|---|---|
| `WEATHER_API` | ✅ | OpenWeatherMap API key | [openweathermap.org](https://openweathermap.org/ap) |
| `NEWS_API` | ✅ | FreeNews APi key | [freenewsapi.io](https://www.freenewsapi.io/) |
| `EMAIL_USER` | ✅ | Gmail address | — |
| `EMAIL_PASS` | ✅ | Gmail **App Password** | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) |
| `DEFAULT_CITY` | ❌ | Default weather city (default: `Kolkata`) | — |
| `TELEGRAM_TOKEN` | ❌ | Bot token from `@BotFather` | [t.me/BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | ❌ | Your chat ID from `@userinfobot` | [t.me/userinfobot](https://t.me/userinfobot) |
| `VOICE_INDEX` | ❌ | Which system voice to use (0, 1, 2...) | — |
| `SPEECH_RATE` | ❌ | Speaking speed (default: `180`) | — |
| `USE_WAKE_WORD` | ❌ | `true` / `false` — passive listening | — |
| `WAKE_WORD` | ❌ | Trigger word (default: `jarvis`) | — |
| `MUSIC_DIR` | ❌ | Folder for `play music` | — |
| `FACES_DIR` | ❌ | Where face encodings live (default: `known_faces`) | — |
| `USER_NAME` | ❌ | Pre-set your name (skips first-run prompt) | — |
| `BRIEFING_TIME` | ❌ | Morning briefing time (default: `08:00`) | — |
| `WATER_REMINDER_MINUTES` | ❌ | Water reminder interval (default: `60`) | — |
| `LOG_LEVEL` | ❌ | `DEBUG`, `INFO`, `WARNING`, `ERROR` | — |

### 🔐 Getting a Gmail App Password

Google blocks plain SMTP logins. You **must** use an App Password:

1. Enable 2-Step Verification on your Google account
2. Visit [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Generate a new app password for "Mail"
4. Copy the 16-character code into `EMAIL_PASS`

---

## 📱 Telegram Remote

Control Jarvis from your phone. **100% free, unlimited.**

### Setup

1. Open Telegram, message **[@BotFather](https://t.me/BotFather)**
2. Send `/newbot` → follow prompts → copy the **token**
3. Message **[@userinfobot](https://t.me/userinfobot)** → copy your **Chat ID**
4. Add both to `.env`:
   ```env
   TELEGRAM_TOKEN=8925605483:ABCdef...
   TELEGRAM_CHAT_ID=1706833970
   ```
5. Restart `python main.py` — you'll see `Telegram bot online.`
6. Send your bot a message like `news` or `weather in Delhi`

### Notes
- Only **one-shot commands** work cleanly over Telegram (no follow-up questions)
- Close any open browser tab on `api.telegram.org/.../getUpdates` — it steals messages
- To send proactive alerts (reminders, battery warnings) to Telegram, set `_remote_buffer` before calling `speak()`

---

## 🎯 Wake Word Setup

Make Jarvis listen passively — no need to press a button.

### 1. Download a Vosk model

| Model | Size | Accuracy | Link |
|---|---|---|---|
| Small English | ~40 MB | Decent | [Download](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip) |
| Large English | ~1.8 GB | Excellent | [Download](https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip) |

### 2. Extract

Unzip and place the folder in your project root:

```
Jarvis Enhanced/
├── vosk-model-small-en-us-0.15/
│   ├── am/
│   ├── conf/
│   └── ...
├── main.py
└── ...
```

### 3. Enable in `.env`

```env
USE_WAKE_WORD=true
WAKE_WORD=jarvis
```

Now say **"Jarvis"** and Jarvis will wake up and listen.

> **Custom wake word:** Change `WAKE_WORD` to anything — `computer`, `friday`, `alexa`, etc.

---

## 📁 Project Structure

```
Jarvis Enhanced/
├── .env                    # 🔒 Secrets (gitignored)
├── .env.example            # Template for new users
├── .gitignore              # Keeps secrets & data out of git
├── README.md               # This file
├── LICENSE                 # MIT
├── requirements.txt        # Python dependencies
│
├── main.py                 # 🎯 Orchestrator — entry point
├── config.py               # Environment loader + validation
├── utils.py                # Logger + safe_eval (no raw eval)
├── router.py               # Regex command dispatcher
├── responses.py            # Capability list + chit-chat replies
│
├── speech.py               # TTS (threaded) + SpeechRecognition
├── api_services.py         # Weather, News, Wikipedia
├── email_service.py        # SMTP wrapper
├── system_controls.py      # System info, screenshot, apps, music
├── system_ext.py           # Volume, brightness, power, files, dictation
├── vision.py               # Face recognition, OCR, QR, motion
├── productivity.py         # To-dos, notes, Pomodoro, habits, briefing
├── personality.py          # Name memory, greetings, mood detection
├── telegram_bot.py         # Remote control via Telegram
├── wake_word.py            # Optional Vosk passive listening
│
├── contacts.json           # 🔒 Your contacts (gitignored)
├── todos.json              # 🔒 Your tasks (gitignored)
├── habits.json             # 🔒 Your habits (gitignored)
├── notes.md                # 🔒 Your notes (gitignored)
├── user.json               # 🔒 Your name + prefs (gitignored)
├── face_encodings.pkl      # 🔒 Biometric data (gitignored)
└── known_faces/            # 🔒 Face images (gitignored)
```

---

## 🐛 Troubleshooting

<details>
<summary><b>🔇 Jarvis prints text but doesn't speak</b></summary>

This is a known `pyttsx3` threading bug on Windows. The fix is to **initialize the engine inside the same thread that calls `runAndWait()`**. This project already does that in `speech.TTSEngine`. If you still have issues:

1. Check `VOICE_INDEX` in `.env` — try `0`, `1`, `2`
2. Test SAPI directly: `Control Panel → Speech Recognition → Text to Speech → Preview Voice`
3. Disable **Nahimic** or **Realtek audio enhancements** (common culprit)
4. Fallback: `pip install pywin32` and use `win32com.client.Dispatch("SAPI.SpVoice")`
</details>

<details>
<summary><b>❌ <code>ImportError: cannot import name 'Application'</code></b></summary>

You have an old `python-telegram-bot` (v13). Upgrade:
```bash
pip uninstall python-telegram-bot
pip install "python-telegram-bot>=21"
```
</details>

<details>
<summary><b>📱 Telegram bot not replying</b></summary>

1. **Close the browser tab** at `api.telegram.org/.../getUpdates` — it steals messages
2. Verify token: `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(len(os.getenv('TELEGRAM_TOKEN','')))"` → should be ~46
3. Ensure `TELEGRAM_CHAT_ID` matches the number from `@userinfobot`
4. Restart `main.py` after editing `.env`
</details>

<details>
<summary><b>🎤 Microphone not detected</b></summary>

1. Windows: Settings → Privacy → Microphone → allow desktop apps
2. Test with: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`
3. Adjust `energy_threshold` in `speech.py` if recognition is flaky
</details>

<details>
<summary><b>👁️ Face recognition install fails (dlib)</b></summary>

`face_recognition` needs `dlib`, which needs `cmake`:
```bash
pip install cmake
pip install dlib
pip install face_recognition
```

**Windows shortcut:** grab a prebuilt `dlib` wheel from [Gohlke's repo](https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib) that matches your Python version.
</details>

<details>
<summary><b>📄 OCR returns empty / errors</b></summary>

Install **Tesseract** separately:
- Windows: [UB-Mannheim build](https://github.com/UB-Mannheim/tesseract/wiki)
- Add install folder (e.g. `C:\Program Files\Tesseract-OCR`) to PATH
- Verify: `tesseract --version`
</details>

<details>
<summary><b>💥 <code>WARNING: Ignoring invalid distribution ~ensorflow</code></b></summary>

Harmless leftover from a failed TensorFlow install. Delete the folder:
```
E:\python\Lib\site-packages\~ensorflow*
```
</details>

---

## 🔒 Privacy

- **All processing is local.** No data leaves your machine unless you explicitly:
  - Use Google STT (sends audio to Google)
  - Enable Telegram (sends commands to Telegram servers)
  - Fetch weather/news (sends city queries to their APIs)
- **No telemetry, no analytics, no tracking.**
- **Secrets stay in `.env`** — never committed to git.
- **Face encodings** are stored as a local pickle file. Delete `face_encodings.pkl` and `known_faces/` to erase biometric data.
- **Full offline mode:** Use Vosk STT + Ollama LLM + pyttsx3 TTS. Zero network calls.

---

## 🛠️ Tech Stack

| Layer | Library | Purpose |
|---|---|---|
| TTS | `pyttsx3` | Text-to-speech |
| STT | `SpeechRecognition` + Google / Vosk | Speech-to-text |
| Wake Word | `vosk` | Offline keyword spotting |
| Weather | `requests` → OpenWeatherMap | Free weather API |
| News | `requests` → NewsAPI | Free news API |
| Email | `smtplib` (stdlib) | Gmail SMTP |
| System | `psutil`, `pyautogui`, `pycaw`, `screen-brightness-control` | OS control |
| Vision | `opencv-python`, `face_recognition`, `pytesseract`, `pyzbar` | Camera + OCR |
| Remote | `python-telegram-bot` | Telegram bot |
| Config | `python-dotenv` | `.env` loading |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m "Add amazing feature"`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

**Please:**
- Never commit `.env` or any file listed in `.gitignore`
- Keep the module split clean — one responsibility per file
- Test on Windows before submitting

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) — offline TTS
- [Vosk](https://alphacephei.com/vosk/) — offline speech recognition
- [python-telegram-bot](https://python-telegram-bot.org/) — Telegram API wrapper
- [OpenWeatherMap](https://openweathermap.org/) & [NewsAPI](https://newsapi.org/) — free data
- The open-source community ❤️

---

<div align="center">

**⭐ If this project helped you, consider giving it a star! ⭐**

*Built with ❤️ and a lot of Python.*

</div>
