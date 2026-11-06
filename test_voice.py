import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print(f"Found {len(voices)} voices. Testing them now...\n")
for i, voice in enumerate(voices):
    print(f"Testing Voice {i}: {voice.name}")
    engine.setProperty('voice', voice.id)
    engine.say(f"Hello Mr. Stark, I am voice number {i}")
    engine.runAndWait()