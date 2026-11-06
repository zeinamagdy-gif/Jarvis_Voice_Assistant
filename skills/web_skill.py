import webbrowser
from core import CONFIG
from . import skill, after


@skill("open")
def open_site(text):
    name = after(text, "open")
    url = CONFIG["sites"].get(name)
    if not url:
        return f"I don't know how to open {name}. Add it to config.json."
    webbrowser.open(url)
    return f"Opening {name}"


@skill("search for")
def search(text):
    query = after(text, "search for")
    webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))
    return f"Searching for {query}"
