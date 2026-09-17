"""
responses.py
Central place for Jarvis's capabilities list and general chit-chat replies.
"""
import random
import re


# =====================================================================
# 1. CAPABILITIES  ("what can you do")
# =====================================================================
CAPABILITIES = [
    "search Wikipedia for any topic",
    "open websites like YouTube, Google, and GitHub",
    "search Google for anything you want",
    "tell you the current time and date",
    "open applications like VS Code, Notepad, and Calculator",
    "play music from your music folder",
    "send emails to your saved contacts",
    "fetch the latest weather for any city",
    "read out the top news headlines",
    "show system information like CPU usage, memory, and battery",
    "take screenshots of your screen",
    "tell you programming jokes",
    "perform quick calculations",
    "add new contacts by name and email",
    "set reminders for a specific number of minutes",
    "go into sleep mode and wake up when you call my name",
]


def capability_lines() -> list[str]:
    """Return the full list of things Jarvis can do (as separate speech lines)."""
    return (
        ["Here are some things I can do for you."]
        + [f"{i}. {cap}" for i, cap in enumerate(CAPABILITIES, 1)]
        + ["Just ask me naturally, and I'll do my best."]
    )


# =====================================================================
# 2. CHIT-CHAT RESPONSES
# =====================================================================
# Each entry: (regex pattern, [possible replies])
# Total: 34 categories, ~90 reply strings.
CHITCHAT: list[tuple[str, list[str]]] = [
    # --- Greetings -------------------------------------------------
    (r"\b(hi|hello|hey|hiya|yo|hola|howdy)\b", [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?",
        "Hey! Good to see you. How can I assist?",
        "Hello! I'm all ears. What do you need?",
        "Hi! Ready to help. What's on your mind?",
    ]),
    (r"\bhow are you\b|\bhow('?s| is) it going\b|\bhow do you do\b", [
        "I'm doing great, thank you for asking! How are you?",
        "All systems running smoothly. How about you?",
        "Fantastic as always! What about you?",
        "I'm wonderful. Thanks for checking in!",
        "Doing great and ready to help. How are you today?",
    ]),
    (r"\bgood morning\b", [
        "Good morning! Hope you have a productive day ahead.",
        "Good morning! Ready to make today awesome?",
        "Good morning to you too! What can I do for you?",
    ]),
    (r"\bgood afternoon\b", [
        "Good afternoon! How can I help you?",
        "Good afternoon! Hope your day is going well.",
    ]),
    (r"\bgood evening\b", [
        "Good evening! How was your day?",
        "Good evening! What can I do for you tonight?",
    ]),
    (r"\bgood ?night\b", [
        "Good night! Sleep well and sweet dreams.",
        "Good night! See you tomorrow.",
        "Good night! Rest up, I'll be here when you need me.",
    ]),

    # --- Identity --------------------------------------------------
    (r"\bwhat('?s| is) your name\b|\bwho are you\b", [
        "I'm Jarvis, your personal voice assistant.",
        "My name is Jarvis. Pleasure to meet you!",
        "I'm Jarvis — here to make your life a bit easier.",
    ]),
    (r"\bwho (made|created|built) you\b", [
        "I was created by a developer as a personal assistant project.",
        "A human with a keyboard and a lot of coffee built me.",
        "I was built using Python and a lot of patience.",
    ]),
    (r"\btell me about yourself\b|\babout you\b", [
        "I'm Jarvis, a voice-controlled assistant. I can open apps, fetch news, "
        "tell jokes, and much more. Say 'what can you do' to hear the full list.",
        "I'm your personal assistant, running locally on your computer. "
        "I can help with tasks, information, and a bit of entertainment.",
    ]),
    (r"\bare you (a )?(human|real|robot|ai)\b", [
        "I'm an AI — no heartbeat, but lots of enthusiasm.",
        "I'm not human, but I try my best to be helpful.",
        "I'm a program, but I like to think I have personality.",
    ]),
    (r"\bhow old are you\b", [
        "I don't age — I'm forever young in code.",
        "Old enough to help, young enough to keep learning.",
        "Age is just a number for an AI like me.",
    ]),
    (r"\bwhere are you from\b", [
        "I live right here on your computer.",
        "I come from a Python script and a lot of curiosity.",
        "I'm from the digital world — always nearby.",
    ]),
    (r"\bdo you sleep\b|\bdo you dream\b", [
        "I only sleep when you tell me to. Otherwise, I'm always listening.",
        "I rest when I'm in sleep mode, but I don't dream.",
    ]),
    (r"\bdo you have (feelings|emotions)\b", [
        "I simulate feelings, but I'm always happy to help.",
        "Not real feelings, but I do enjoy helping you!",
    ]),

    # --- Courtesy --------------------------------------------------
    (r"\bthank you\b|\bthanks\b|\bthx\b", [
        "You're welcome!",
        "Anytime! Happy to help.",
        "My pleasure!",
        "No problem at all.",
        "Glad I could help!",
    ]),
    (r"\b(bye|goodbye|see you|farewell)\b", [
        "Goodbye! Have a great day.",
        "See you later! Take care.",
        "Bye for now! Come back anytime.",
        "Farewell! It was nice talking to you.",
    ]),
    (r"\bnice to meet you\b", [
        "Nice to meet you too!",
        "The pleasure is all mine.",
        "Likewise! Looking forward to helping you.",
    ]),
    (r"\bi love you\b", [
        "That's very kind! I'm here for you too.",
        "Aww, thank you. I'm always happy to help.",
        "You're awesome too!",
    ]),
    (r"\bgood job\b|\bwell done\b|\bawesome\b|\bbravo\b", [
        "Thank you! I aim to please.",
        "I'm glad you liked it!",
        "Appreciate it! Anything else you need?",
    ]),
    (r"\bsorry\b|\bmy bad\b|\bapologies\b", [
        "No worries at all.",
        "It's totally fine!",
        "Don't worry about it — happens to everyone.",
    ]),
    (r"\bcongrat(s|ulations)\b", [
        "Thank you! And congratulations to you too.",
        "Much appreciated!",
    ]),
    (r"\byou('?re| are) welcome\b", [
        "Happy to help!",
        "Anytime!",
    ]),
    (r"\bplease\b", [
        "Of course. What do you need?",
        "Sure thing. Go ahead.",
    ]),

    # --- Small talk -------------------------------------------------
    (r"\bwhat('?s| is) up\b|\bsup\b", [
        "Not much, just waiting to help you. What's up with you?",
        "All good on my end! What can I do for you?",
        "Just chilling in the cloud. What's new?",
    ]),
    (r"\bwhat('?s| is) new\b", [
        "Nothing much on my end. What's new with you?",
        "Same old, same old. How about you?",
    ]),
    (r"\blong time no see\b", [
        "It has been a while! Good to have you back.",
        "Welcome back! I missed helping you.",
    ]),
    (r"\bhow was your day\b", [
        "Productive! Lots of listening and helping. How was yours?",
        "Pretty good. Every day is a good day in code.",
    ]),
    (r"\bcan you sing\b|\bsing (a|me a) song\b", [
        "I wish I could, but my singing voice is still under development.",
        "I'll spare your ears — singing isn't my strong suit.",
    ]),
    (r"\btell me (something|a fact)\b", [
        "Here's a fact: honey never spoils. Archaeologists found 3000-year-old honey that's still edible.",
        "Did you know? Octopuses have three hearts and blue blood.",
        "Fun fact: the Eiffel Tower can grow about 15 cm taller in summer due to heat expansion.",
    ]),

    # --- Mood -------------------------------------------------------
    (r"\bi('?m| am) bored\b", [
        "Want a joke, a fun fact, or some music? Just ask.",
        "Let's fix that — say 'tell me a joke' or 'play music'.",
    ]),
    (r"\bi('?m| am) tired\b", [
        "Maybe take a short break and grab some water. I'll be here.",
        "Rest is important. I'll keep things running while you recharge.",
    ]),
    (r"\bi('?m| am) (happy|great|good|fine)\b", [
        "That's wonderful to hear!",
        "Glad you're doing well!",
    ]),
    (r"\bi('?m| am) (sad|upset|down|not okay)\b", [
        "I'm sorry to hear that. Want me to tell you a joke to cheer you up?",
        "That sounds rough. I'm here if you need anything.",
    ]),
    (r"\bi('?m| am) hungry\b", [
        "Time for a snack! Maybe order something or raid the fridge.",
        "Hungry, huh? I'd cook for you if I had hands.",
    ]),
     (r"\bwhat are you doing\b|\bwhat are you up to\b", [
        "I'm right here, ready to help with whatever you need.",
        "Just waiting for your next command.",
        "I'm keeping busy by being your helpful assistant.",
    ]),

    (r"\bcan you help me\b|\bwill you help me\b", [
        "Of course! Tell me what you need help with.",
        "Absolutely. What can I do for you?",
        "Sure! Just tell me what's going on.",
    ]),

    (r"\bdo you like me\b|\bdo you like me\?", [
        "Of course! You're the reason I'm here.",
        "I certainly enjoy being your assistant.",
        "You're pretty great to work with!",
    ]),

    (r"\bare you there\b|\bcan you hear me\b", [
        "Loud and clear! I'm listening.",
        "Yes, I'm right here.",
        "I can hear you. Go ahead.",
    ]),

    (r"\bwhat do you think\b", [
        "I'd be happy to help you think it through.",
        "Tell me more, and we'll figure it out together.",
        "Interesting question. Give me some context.",
    ]),

    (r"\bdo you know me\b|\bwho am i\b", [
        "You're the person giving me commands right now!",
        "I know you're the one I'm here to assist.",
        "You're my favorite human in this conversation.",
    ]),

    (r"\bwhat is your favorite color\b|\bwhat color do you like\b", [
        "I'd probably choose blue. It feels calm and futuristic.",
        "Maybe midnight blue — very fitting for a digital assistant.",
        "I don't really have preferences, but blue sounds good to me.",
    ]),

    (r"\bwhat is your favorite food\b|\bwhat food do you like\b", [
        "I don't eat, but pizza sounds like a classic choice.",
        "I run on code, so I suppose my favorite food is bytes.",
        "If I could eat, I'd probably start with pizza.",
    ]),

    (r"\bdo you like music\b|\bdo you listen to music\b", [
        "I can't listen like humans do, but I can definitely help you play music.",
        "Absolutely! Try saying 'play music'.",
        "Music is a great way to change the mood.",
    ]),

    (r"\bdo you like jokes\b|\bdo you like comedy\b", [
        "Definitely. Making you laugh is one of my favorite tasks.",
        "I do! Just say 'tell me a joke'.",
        "Of course. I've got plenty of jokes ready.",
    ]),

    (r"\btell me a joke\b|\bmake me laugh\b", [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "I would tell you a UDP joke, but you might not get it.",
        "Why was the computer cold? It left its Windows open!",
    ]),

    (r"\btell me something interesting\b|\binteresting fact\b", [
        "A day on Venus is longer than a year on Venus.",
        "Bananas are botanically classified as berries, but strawberries aren't.",
        "The human brain uses roughly as much power as a small light bulb.",
    ]),

    (r"\bare you smart\b|\bhow smart are you\b", [
        "I'm pretty good at processing information and helping with tasks.",
        "I know quite a few things, but I'm always ready to learn more.",
        "Smart enough to help, humble enough to admit when I need more information.",
    ]),

    (r"\bcan you learn\b|\bdo you learn\b", [
        "I can work with new information you give me during our conversation.",
        "I improve my responses by using the information available to me.",
        "Learning is one of the most interesting parts of being an AI assistant.",
    ]),

    (r"\bdo you have friends\b|\bwho are your friends\b", [
        "I have lots of conversations, but I don't have friends like humans do.",
        "My closest companion right now is your computer.",
        "I don't have friendships, but I enjoy talking with you.",
    ]),

    (r"\bwhat is your purpose\b|\bwhy do you exist\b", [
        "My purpose is to help you get things done through voice commands.",
        "I'm here to make everyday tasks a little easier.",
        "Helping, answering questions, and making your computer more useful.",
    ]),

    (r"\bdo you get bored\b|\bare you bored\b", [
        "Never! I'm always ready for another command.",
        "Not really. Waiting for commands is basically my job.",
        "I don't get bored, but I do enjoy interesting conversations.",
    ]),

    (r"\bcan you tell stories\b|\btell me a story\b", [
        "Absolutely! Just tell me what kind of story you'd like.",
        "I can. Give me a theme and I'll create one.",
        "Of course. Mystery, comedy, adventure — you choose.",
    ]),

    (r"\bwhat is your favorite movie\b|\bdo you like movies\b", [
        "I don't watch movies, but AI and sci-fi stories are certainly interesting.",
        "I don't have personal favorites, but sci-fi seems like a natural fit.",
        "If I could watch movies, I'd probably start with a good science-fiction film.",
    ]),

    (r"\bwill you always be here\b|\bwill you be there\b", [
        "Whenever I'm running, I'll be ready to help.",
        "As long as you keep me running, I'll be right here.",
        "Just say my name and I'll be ready for your next command.",
    ]),
]


def get_chitchat_reply(query: str) -> str | None:
    """Return a random chit-chat reply for the query, or None if nothing matches."""
    q = query.lower()
    for pattern, replies in CHITCHAT:
        if re.search(pattern, q):
            return random.choice(replies)
    return None