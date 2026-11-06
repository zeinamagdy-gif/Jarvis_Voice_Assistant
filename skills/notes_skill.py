import datetime
from core import DATA_DIR
from . import skill, after


@skill("take a note", "note that")
def take_note(text):
    note = after(text, "take a note", "note that")
    if not note:
        return "What should I write?"
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(DATA_DIR / "notes.txt", "a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {note}\n")
    return "Note saved."
