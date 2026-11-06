import pyttsx3
from . import CONFIG

_engine = pyttsx3.init()
_engine.setProperty("rate", CONFIG["speech_rate"])


def speak(text):
    _engine.say(text)
    _engine.runAndWait()
