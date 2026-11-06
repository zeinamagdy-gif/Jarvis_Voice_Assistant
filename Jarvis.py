import os
import time
import datetime
import webbrowser
import requests
import speech_recognition as sr
import ctypes
import threading
import pygame
import math
import random
import pyautogui
from gtts import gTTS
from duckduckgo_search import DDGS


# ==================== CINEMATIC MOVIE-STYLE HUD ====================
class JarvisHUD:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1200, 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("J.A.R.V.I.S. INTERFACE")
        self.clock = pygame.time.Clock()

        # Colors
        self.bg_color = (5, 10, 20)
        self.cyan = (0, 255, 255)
        self.gold = (255, 170, 0)
        self.dim_cyan = (0, 100, 150)
        self.white = (255, 255, 255)

        # Fonts
        self.font_large = pygame.font.SysFont("consolas", 40, bold=True)
        self.font_medium = pygame.font.SysFont("consolas", 24)
        self.font_small = pygame.font.SysFont("consolas", 18)

        # Animation state
        self.angle1 = 0
        self.angle2 = 0
        self.state = "idle"  # idle, listening, processing, speaking
        self.speak_pulse = 0
        self.audio_bars = [0] * 24
        self.scan_angle = 0

        # Text display
        self.user_text = ""
        self.jarvis_text = ""
        self.text_alpha = 255

        self.running = True

    def draw_hud(self):
        self.screen.fill(self.bg_color)
        cx, cy = self.width // 2, self.height // 2

        self.draw_background_grid()
        self.draw_corners()
        self.draw_rotating_rings(cx, cy)
        self.draw_state_indicator(cx, cy)
        self.draw_center_visualizer(cx, cy)
        self.draw_text_overlays()
        self.draw_conversation_display()

        pygame.display.flip()

    def draw_background_grid(self):
        # Subtle grid lines for tech feel
        for x in range(0, self.width, 50):
            pygame.draw.line(self.screen, (10, 20, 30), (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 50):
            pygame.draw.line(self.screen, (10, 20, 30), (0, y), (self.width, y), 1)

    def draw_corners(self):
        # Camera-style corner brackets
        pygame.draw.lines(self.screen, self.cyan, False, [(30, 100), (30, 30), (100, 30)], 4)
        pygame.draw.lines(self.screen, self.cyan, False,
                          [(self.width - 100, 30), (self.width - 30, 30), (self.width - 30, 100)], 4)
        pygame.draw.lines(self.screen, self.cyan, False,
                          [(30, self.height - 100), (30, self.height - 30), (100, self.height - 30)], 4)
        pygame.draw.lines(self.screen, self.cyan, False,
                          [(self.width - 100, self.height - 30), (self.width - 30, self.height - 30),
                           (self.width - 30, self.height - 100)], 4)

    def draw_rotating_rings(self, cx, cy):
        # Outer segmented ring (rotates clockwise)
        for i in range(12):
            angle = math.radians(self.angle1 + i * 30)
            x1 = cx + 220 * math.cos(angle)
            y1 = cy + 220 * math.sin(angle)
            x2 = cx + 240 * math.cos(angle)
            y2 = cy + 240 * math.sin(angle)
            pygame.draw.line(self.screen, self.cyan, (x1, y1), (x2, y2), 3)

        # Inner dashed ring (rotates counter-clockwise)
        for i in range(36):
            angle = math.radians(self.angle2 + i * 10)
            x1 = cx + 170 * math.cos(angle)
            y1 = cy + 170 * math.sin(angle)
            x2 = cx + 180 * math.cos(angle)
            y2 = cy + 180 * math.sin(angle)
            pygame.draw.line(self.screen, self.dim_cyan, (x1, y1), (x2, y2), 2)

        self.angle1 = (self.angle1 + 1) % 360
        self.angle2 = (self.angle2 - 2) % 360

    def draw_state_indicator(self, cx, cy):
        # Scanning effect when listening
        if self.state == "listening":
            self.scan_angle = (self.scan_angle + 3) % 360
            # Draw scanning line
            end_x = cx + 150 * math.cos(math.radians(self.scan_angle))
            end_y = cy + 150 * math.sin(math.radians(self.scan_angle))
            pygame.draw.line(self.screen, self.gold, (cx, cy), (end_x, end_y), 3)

            # Pulsing circle
            pulse = abs(math.sin(time.time() * 3)) * 20
            pygame.draw.circle(self.screen, self.gold, (cx, cy), int(150 + pulse), 2)

    def draw_center_visualizer(self, cx, cy):
        base_radius = 100

        if self.state == "speaking":
            self.speak_pulse = min(self.speak_pulse + 8, 50)
            self.audio_bars = [random.randint(20, 80) for _ in range(24)]
        elif self.state == "listening":
            self.speak_pulse = min(self.speak_pulse + 3, 20)
            self.audio_bars = [random.randint(5, 30) for _ in range(24)]
        else:
            self.speak_pulse = max(self.speak_pulse - 3, 0)
            self.audio_bars = [max(0, b - 3) for b in self.audio_bars]

        radius = base_radius + self.speak_pulse

        # Central core
        pygame.draw.circle(self.screen, self.bg_color, (cx, cy), radius)

        # Core outline color based on state
        if self.state == "listening":
            core_color = self.gold
        elif self.state == "speaking":
            core_color = self.cyan
        else:
            core_color = self.dim_cyan

        pygame.draw.circle(self.screen, core_color, (cx, cy), radius, 3)

        # Audio visualizer bars
        for i in range(24):
            angle = math.radians(i * 15)
            bar_len = self.audio_bars[i]
            x1 = cx + (radius + 15) * math.cos(angle)
            y1 = cy + (radius + 15) * math.sin(angle)
            x2 = cx + (radius + 15 + bar_len) * math.cos(angle)
            y2 = cy + (radius + 15 + bar_len) * math.sin(angle)

            if self.state == "speaking":
                color = self.gold
            elif self.state == "listening":
                color = self.gold
            else:
                color = self.dim_cyan

            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 4)

    def draw_text_overlays(self):
        # Title
        title = self.font_large.render("J.A.R.V.I.S.", True, self.cyan)
        self.screen.blit(title, (50, 50))

        # Status
        status_map = {
            "idle": "STATUS: STANDBY",
            "listening": "STATUS: LISTENING...",
            "processing": "STATUS: PROCESSING...",
            "speaking": "STATUS: RESPONDING"
        }
        status_text = status_map.get(self.state, "STATUS: ONLINE")
        status_color = self.gold if self.state == "listening" else self.cyan
        status = self.font_medium.render(status_text, True, status_color)
        self.screen.blit(status, (50, 100))

        # System info
        mic_text = "AUDIO INPUT: ACTIVE"
        mic = self.font_small.render(mic_text, True, self.dim_cyan)
        self.screen.blit(mic, (self.width - 300, 50))

        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_text = self.font_small.render(time_str, True, self.dim_cyan)
        self.screen.blit(time_text, (self.width - 300, 80))

    def draw_conversation_display(self):
        # Display user input
        if self.user_text:
            user_label = self.font_small.render("USER INPUT:", True, self.gold)
            self.screen.blit(user_label, (50, self.height - 150))

            # Wrap text if too long
            words = self.user_text.split()
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.font_medium.size(test_line)[0] < self.width - 100:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

            y_offset = self.height - 120
            for line in lines[:2]:  # Show max 2 lines
                text_surface = self.font_medium.render(line, True, self.white)
                self.screen.blit(text_surface, (50, y_offset))
                y_offset += 30

        # Display Jarvis response
        if self.jarvis_text:
            jarvis_label = self.font_small.render("JARVIS RESPONSE:", True, self.cyan)
            self.screen.blit(jarvis_label, (50, self.height - 80))

            # Wrap text
            words = self.jarvis_text.split()
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.font_medium.size(test_line)[0] < self.width - 100:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

            y_offset = self.height - 50
            for line in lines[:2]:  # Show max 2 lines
                text_surface = self.font_medium.render(line, True, self.cyan)
                self.screen.blit(text_surface, (50, y_offset))
                y_offset += 30

    def set_state(self, state):
        self.state = state

    def set_user_text(self, text):
        self.user_text = text

    def set_jarvis_text(self, text):
        self.jarvis_text = text

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.draw_hud()
            self.clock.tick(60)
        pygame.quit()


# ==================== JARVIS CORE LOGIC ====================
class JarvisCore:
    def __init__(self, hud):
        self.hud = hud
        self.recognizer = sr.Recognizer()
        self.history = []
        self.awake = False
        self.last_activity = time.time()

        pygame.mixer.init()
        pyautogui.FAILSAFE = False

    def speak(self, text):
        print("Jarvis:", text)
        self.hud.set_jarvis_text(text)  # Display on screen
        self.hud.set_state("speaking")
        try:
            temp_file = f"jarvis_temp_{int(time.time() * 1000)}.mp3"
            tts = gTTS(text=text, lang='en', tld='com.au')
            tts.save(temp_file)

            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            try:
                pygame.mixer.music.unload()
            except AttributeError:
                pass

            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except PermissionError:
                    pass
        except Exception as e:
            print(f"Audio Error: {e}")
        finally:
            self.hud.set_state("idle")

    def listen(self, timeout=5, phrase_limit=10):
        self.hud.set_state("listening")  # Show listening state
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
                text = self.recognizer.recognize_google(audio).lower()
                print("You:", text)
                self.hud.set_user_text(text)  # Display on screen
                return text
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return ""
        finally:
            self.hud.set_state("idle")

    def search_google(self, query):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if results:
                    summary = "Here's what I found: "
                    for i, result in enumerate(results, 1):
                        summary += f"{i}. {result['title']}. "
                    return summary
                return "I couldn't find any results for that."
        except Exception as e:
            return f"Search failed: {str(e)}"

    def search_spotify_and_play(self, song_query):
        try:
            search_url = f"https://open.spotify.com/search/{song_query.replace(' ', '%20')}"
            webbrowser.open(search_url)
            time.sleep(3)
            pyautogui.press('space')
            return f"Searching Spotify for {song_query}"
        except Exception as e:
            return f"Spotify search failed: {str(e)}"

    def open_notepad_and_type(self, text_to_write):
        try:
            os.startfile("notepad.exe")
            time.sleep(1)
            pyautogui.write(text_to_write, interval=0.05)
            return f"Opening Notepad and writing: {text_to_write}"
        except Exception as e:
            return f"Notepad automation failed: {str(e)}"

    def get_weather(self, location=""):
        try:
            if location:
                url = f"https://wttr.in/{location}?format=3"
            else:
                url = "https://wttr.in/?format=3"

            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                weather_text = response.text.strip()
                return f"The weather is {weather_text}"
            return "I couldn't fetch the weather data."
        except Exception as e:
            return f"Weather check failed: {str(e)}"

    def handle_command(self, text):
        text = text.lower().strip()

        if "volume up" in text or "louder" in text:
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0);
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
            return "Volume increased."
        if "volume down" in text or "quieter" in text:
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0);
            ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
            return "Volume decreased."

        if "play music" in text or "play spotify" in text:
            os.startfile("spotify:")
            time.sleep(2)
            ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0);
            ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0)
            return "Playing music on Spotify."

        if "play" in text and ("song" in text or "music" in text or "track" in text):
            song = text.replace("play", "").replace("song", "").replace("music", "").replace("track", "").replace(
                "on spotify", "").strip()
            if song:
                return self.search_spotify_and_play(song)

        if "next song" in text or "skip" in text:
            ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0);
            ctypes.windll.user32.keybd_event(0xB0, 0, 2, 0)
            return "Skipping to next song."
        if text in ["pause", "stop music"]:
            ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0);
            ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0)
            return "Paused."

        if "time" in text: return "It is " + datetime.datetime.now().strftime("%I:%M %p")
        if "date" in text or "today" in text: return "Today is " + datetime.datetime.now().strftime("%A, %B %d")

        if "weather" in text:
            location = text.replace("weather", "").replace("what's the", "").replace("what is the", "").replace("in",
                                                                                                                "").strip()
            return self.get_weather(location)

        if "search" in text or "google" in text:
            query = text.replace("search", "").replace("google", "").replace("for", "").replace("on google", "").strip()
            if query:
                return self.search_google(query)

        if "write" in text and "notepad" in text:
            write_text = text.replace("write", "").replace("in notepad", "").replace("on notepad", "").strip()
            if write_text:
                return self.open_notepad_and_type(write_text)

        if text.startswith("open"):
            name = text.replace("open", "", 1).strip().replace("the", "").strip()
            if name == "spotify":
                os.startfile("spotify:"); return "Opening Spotify."
            elif name == "notepad":
                os.startfile("notepad.exe"); return "Opening Notepad."
            elif name == "youtube":
                webbrowser.open("https://www.youtube.com"); return "Opening YouTube."
            elif name == "gmail":
                webbrowser.open("https://mail.google.com"); return "Opening Gmail."
            elif name == "google":
                webbrowser.open("https://www.google.com"); return "Opening Google."

        return None

    def ask_ai(self, question):
        self.hud.set_state("processing")  # Show processing state
        self.history.append({"role": "user", "content": question})
        messages = self.history[-10:]
        try:
            r = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3.2",
                    "messages": [{"role": "system",
                                  "content": "You are Jarvis, a helpful voice assistant. Keep answers short (1-3 sentences) because they will be spoken aloud."}] + messages,
                    "stream": False,
                },
                timeout=120,
            )
            answer = r.json()["message"]["content"]
            self.history.append({"role": "assistant", "content": answer})
            return answer
        except Exception:
            return "I cannot connect to my brain. Please make sure Ollama is running."

    def listen_loop(self):
        self.speak("Welcome Back Zeina")
        while True:
            heard = self.listen()
            if not heard:
                if self.awake and time.time() - self.last_activity > 15:
                    self.awake = False
                continue

            if "jarvis" in heard:
                self.awake = True
                self.last_activity = time.time()
                command = heard.split("jarvis", 1)[1].strip()
                if not command:
                    self.speak("Yes, how can I help you today?")
                    continue
            elif self.awake:
                command = heard
                self.last_activity = time.time()
            else:
                continue

            if any(w in command for w in ("stop", "exit", "goodbye", "shut down")):
                self.speak("Goodbye!")
                break

            reply = self.handle_command(command)
            if reply is None:
                reply = self.ask_ai(command)
            self.speak(reply)


# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    import glob

    for old_file in glob.glob("jarvis_temp_*.mp3"):
        try:
            os.remove(old_file)
        except:
            pass

    hud = JarvisHUD()
    jarvis = JarvisCore(hud)

    threading.Thread(target=jarvis.listen_loop, daemon=True).start()
    hud.run()
