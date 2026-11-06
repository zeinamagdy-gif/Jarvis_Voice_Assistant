"""
Skill system. To add a feature, create a new .py file in this folder:

    from . import skill

    @skill("trigger phrase", "another trigger")
    def my_skill(text):
        return "What Jarvis says back"

Every .py file here is loaded automatically.
"""
import importlib
import pkgutil
import re
from difflib import SequenceMatcher
SKILLS = []



def _fuzzy(trigger, text, threshold=0.85):
    n = len(trigger.split())
    words = text.split()
    for i in range(len(words) - n + 1):
        window = " ".join(words[i:i + n])
        if SequenceMatcher(None, trigger, window).ratio() >= threshold:
            return True
    return False




def skill(*triggers):
    def decorator(fn):
        SKILLS.append({"name": fn.__name__, "triggers": [t.lower() for t in triggers], "fn": fn})
        return fn
    return decorator


def after(text, *phrases):
    """Return the text that comes after the first matching phrase."""
    for p in phrases:
        if p in text:
            return text.split(p, 1)[1].strip()
    return ""


def load_skills():
    for module in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module.name}")

def dispatch(text):
    # Pass 1: exact whole-word match
    for s in SKILLS:
        for t in s["triggers"]:
            if re.search(r"\b" + re.escape(t) + r"\b", text):
                result = s["fn"](text)
                if result is not None:
                    return result
    # Pass 2: near matches, only for longer triggers so short words don't misfire
    for s in SKILLS:
        for t in s["triggers"]:
            if len(t) >= 6 and _fuzzy(t, text):
                result = s["fn"](text)
                if result is not None:
                    return result
    return None
