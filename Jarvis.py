"""
Simple Jarvis voice assistant (starter version)

Setup:
    python -m venv venv
    venv\\Scripts\\activate          (Windows)   |   source venv/bin/activate (Mac/Linux)
    pip install SpeechRecognition pyttsx3 PyAudio requests anthropic

Brain options (set BRAIN below):
    "ollama"  -> free, runs locally (install Ollama, then: ollama pull llama3.2)
    "claude"  -> needs ANTHROPIC_API_KEY environment variable (paid API)
"""

import os
import datetime
import webbrowser

import requests
import pyttsx3
import speech_recognition as sr

BRAIN = "ollama"                  # "ollama" or "claude"
WAKE_WORD = "jarvis"
OLLAMA_MODEL = "llama3.2"
CLAUDE_MODEL = "claude-sonnet-5-5"

SYSTEM_PROMPT = (
    "You are Jarvis, a helpful voice assistant. "
    "Keep answers short (1-3 sentences) because they will be spoken aloud."
)

# ---------- Mouth ----------
engine = pyttsx3.init()
engine.setProperty("rate", 175)


def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()


# ---------- Ears ----------
recognizer = sr.Recognizer()


def listen(timeout=5, phrase_limit=10):
    """Listen once and return the recognized text (lowercase), or ''."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            return ""
    try:
        text = recognizer.recognize_google(audio)  # needs internet
        print("You:", text)
        return text.lower()
    except (sr.UnknownValueError, sr.RequestError):
        return ""


# ---------- Brain ----------
history = []


def ask_ai(question):
    history.append({"role": "user", "content": question})
    messages = history[-10:]  # keep short memory

    if BRAIN == "ollama":
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                "stream": False,
            },
            timeout=120,
        )
        answer = r.json()["message"]["content"]
    else:
        import anthropic
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        resp = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        answer = resp.content[0].text

    history.append({"role": "assistant", "content": answer})
    return answer


# ---------- Hands (safe, whitelisted commands only) ----------
SITES = {
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
}


def handle_command(text):
    """Return a reply if this was a built-in command, else None."""
    if "time" in text:
        return "It is " + datetime.datetime.now().strftime("%I:%M %p")
    if "date" in text or "today" in text:
        return "Today is " + datetime.datetime.now().strftime("%A, %B %d")
    if text.startswith("open "):
        name = text.replace("open ", "", 1).strip()
        if name in SITES:
            webbrowser.open(SITES[name])
            return f"Opening {name}"
        return f"I don't know how to open {name} yet"
    if text.startswith("search for "):
        query = text.replace("search for ", "", 1)
        webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))
        return f"Searching for {query}"
    return None


# ---------- Main loop ----------
def main():
    speak("Welcome Back Mr. stark")
    while True:
        heard = listen()
        if WAKE_WORD not in heard:
            continue

        command = heard.split(WAKE_WORD, 1)[1].strip()
        if not command:
            speak("Yes, how can i help you today?")
            command = listen()
            if not command:
                continue

        if any(w in command for w in ("stop", "exit", "goodbye", "shut down")):
            speak("Goodbye!")
            break

        reply = handle_command(command)
        if reply is None:
            try:
                reply = ask_ai(command)
            except Exception as e:
                reply = "Sorry, my brain is not responding."
                print("Error:", e)
        speak(reply)


if __name__ == "__main__":
    main()