import os
import platform
import subprocess
from core import CONFIG
from . import skill, after

from difflib import get_close_matches

# replace the line:  app = CONFIG.get("apps", {}).get(name)

@skill("open", "launch", "start")
def open_app(text):
    name = after(text, "open", "launch", "start")
    apps = CONFIG.get("apps", {})
    match = get_close_matches(name, apps.keys(), n=1, cutoff=0.7)
    app = apps[match[0]] if match else None
    if app is None:
        return None  # not an app, let the next skill try (e.g. websites)

    system = platform.system()
    try:
        if system == "Windows" and "windows" in app:
            os.startfile(app["windows"])
        elif system == "Darwin" and "mac" in app:
            subprocess.Popen(["open", "-a", app["mac"]])
        elif system == "Linux" and "linux" in app:
            subprocess.Popen([app["linux"]])
        else:
            return f"I don't have {name} set up for your system."
    except Exception as e:
        print("Error:", e)
        return f"I couldn't open {name}."
    return f"Opening {name}"