# core/mouth.py
import pyttsx3
from core import CONFIG

# Initialize engine
engine = pyttsx3.init()

# Force it to use a valid system voice (Fixes the "silent" bug)
voices = engine.getProperty('voices')
if voices:
    # voices[0] is usually male, voices[1] is usually female (depending on OS)
    engine.setProperty('voice', voices[0].id)

# Set the speed from your config
engine.setProperty('rate', CONFIG.get('speech_rate', 175))

def speak(text):
    """Speaks the text out loud."""
    if not text:
        return
    try:
        engine.say(text)
        engine.runAndWait()
    except RuntimeError:
        # Sometimes pyttsx3 crashes if called too fast in a loop
        pass
    except Exception as e:
        print(f"[MOUTH ERROR] TTS failed: {e}")
