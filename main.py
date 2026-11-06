import sys
import time
from core import CONFIG, brain
from skills import load_skills, dispatch
import logging
from core import ROOT

logging.basicConfig(filename=ROOT / "jarvis.log", level=logging.INFO,
                    format="%(asctime)s %(message)s")
logging.getLogger("comtypes").setLevel(logging.WARNING)   # hides the noisy startup lines
TEXT_MODE = "--text" in sys.argv
AWAKE_SECONDS = 15   # how long it stays awake after your last command

if TEXT_MODE:
    def say(t): print("Jarvis:", t)
    def hear(): return input("You: ").lower().strip()
else:
    from core import mouth, ears
    def say(t):
        print("Jarvis:", t)
        mouth.speak(t)
    def hear():
        heard = ears.listen()
        if heard:
            print("Heard:", heard)
        return heard


def find_wake_word(heard):
    for w in CONFIG["wake_words"]:
        if w in heard:
            return w
    return None


def respond(command):
    reply = dispatch(command)
    if reply is None:
        try:
            reply = brain.ask(command)
        except Exception as e:
            print("Error:", e)
            reply = "Sorry, my brain is not responding."
    return reply


def main():
    load_skills()
    say("Welcome back mr. Stark")
    awake = False
    last_activity = 0

    while True:
        heard = hear()

        if TEXT_MODE:
            command = heard
        else:
            if awake and time.time() - last_activity > AWAKE_SECONDS:
                awake = False
                print("(sleeping)")

            wake = find_wake_word(heard) if heard else None
            if wake:
                awake = True
                command = heard.split(wake, 1)[1].strip()
                if not command:
                    say("Yes, how can i help you today?")
                    last_activity = time.time()
                    continue
            elif awake and heard:
                command = heard        # no wake word needed while awake
            else:
                continue

        if not command:
            continue
        if any(p in command for p in ("goodbye", "shut down", "exit")):
            say("Goodbye!")
            break
        if any(p in command for p in ("that's all", "thank you", "go to sleep")):
            awake = False
            say("Standing by.")
            continue

        say(respond(command))
        last_activity = time.time()


if __name__ == "__main__":
    main()