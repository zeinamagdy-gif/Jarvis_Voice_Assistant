import numpy as np
import speech_recognition as sr
from faster_whisper import WhisperModel
from . import CONFIG
import re   # add at the top


_recognizer = sr.Recognizer()
_recognizer.dynamic_energy_threshold = True
_recognizer.pause_threshold = 0.8          # seconds of silence that ends a phrase
_mic = sr.Microphone()

with _mic as source:
    _recognizer.adjust_for_ambient_noise(source, duration=1)

# "base" is fast; use "small" for better accuracy if your laptop can handle it
_model = WhisperModel(CONFIG.get("whisper_model", "base"), device="cpu", compute_type="int8")

# Hints help Whisper recognize your wake word and common commands
_HINT = "Jarvis, open Spotify, add task, list tasks, take a note, what time is it"

def _clean(text):
    text = text.lower()
    text = re.sub(r"[^\w\s']", " ", text)    # remove punctuation, keep apostrophes
    return re.sub(r"\s+", " ", text).strip()
def listen(timeout=5, phrase_limit=10):
    with _mic as source:
        try:
            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            return ""
        text = " ".join(s.text for s in segments)
        return _clean(text)

    raw = audio.get_raw_data(convert_rate=16000, convert_width=2)
    samples = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0

    segments, _ = _model.transcribe(
        samples,
        language=CONFIG.get("whisper_language", "en"),   # "ar" for Arabic, None to auto-detect
        beam_size=5,
        vad_filter=True,            # ignores silence, which prevents made-up text
        initial_prompt=_HINT,
    )
    return " ".join(s.text for s in segments).lower().strip().strip(".!?")