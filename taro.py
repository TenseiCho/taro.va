import speech_recognition as sr
import pyttsx3
import threading
import tkinter as tk
from datetime import datetime, timedelta
import pygame
import re
import time

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.wake_word = "taro"
        self.is_listening = False
        pygame.mixer.init()
        self.wake_sound = pygame.mixer.Sound("start.wav")
        self.timer_sound = pygame.mixer.Sound("gameover.wav")
        self.timer_end_time = None
        self.timer_thread = None

    def play_wake_sound(self):
        pygame.mixer.Sound.play(self.wake_sound)

    def play_timer_sound(self):
        pygame.mixer.Sound.play(self.timer_sound)

    def listen_for_wake_word(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=1)
                    text = self.recognizer.recognize_google(audio).lower()
                    if self.wake_word in text:
                        self.is_listening = True
                        self.play_wake_sound()
                        self.process_command()
                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    print("Could not request results from speech recognition service")

    def process_command(self):
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)
            try:
                command = self.recognizer.recognize_google(audio).lower()
                if "what time is it" in command or "tell me the time" in command:
                    self.tell_time()
                elif "set a timer" in command:
                    self.set_timer(command)
                elif "cancel the timer" in command:
                    self.cancel_timer()
                else:
                    self.speak(f"You said: {command}")
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't understand that.")
            except sr.RequestError:
                self.speak("Sorry, I'm having trouble processing your request.")
        self.is_listening = False

    def tell_time(self):
        current_time = datetime.now().strftime("%I:%M %p")
        self.speak(f"The current time is {current_time}")

    def set_timer(self, command):
        minutes = 0
        hours = 0
        
        # Extract minutes and hours from the command
        minute_match = re.search(r'(\d+)\s*minute', command)
        hour_match = re.search(r'(\d+)\s*hour', command)
        
        if minute_match:
            minutes = int(minute_match.group(1))
        if hour_match:
            hours = int(hour_match.group(1))
        
        if minutes == 0 and hours == 0:
            self.speak("I'm sorry, I couldn't understand the timer duration. Please try again.")
            return
        
        total_seconds = minutes * 60 + hours * 3600
        self.timer_end_time = datetime.now() + timedelta(seconds=total_seconds)
        
        # Construct the timer message
        timer_message = []
        if hours > 0:
            timer_message.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            timer_message.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        
        timer_str = " and ".join(timer_message)
        self.speak(f"Timer set for {timer_str}.")
        
        if self.timer_thread is not None and self.timer_thread.is_alive():
            self.timer_thread.cancel()
        
        self.timer_thread = threading.Timer(total_seconds, self.timer_finished)
        self.timer_thread.start()
    
    def cancel_timer(self):
        if self.timer_thread is not None and self.timer_thread.is_alive():
            self.timer_thread.cancel()
            self.timer_end_time = None
            self.speak("Timer cancelled.")
        else:
            self.speak("There is no active timer to cancel.")

    def timer_finished(self):
        self.play_timer_sound()
        self.timer_end_time = None

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def run_gui(self):
        root = tk.Tk()
        root.title("Taro Voice Assistant")
        root.geometry("300x150")

        status_label = tk.Label(root, text="Status: Waiting for wake word")
        status_label.pack(pady=10)

        timer_label = tk.Label(root, text="No active timer")
        timer_label.pack(pady=10)

        def update_gui():
            status = "Listening" if self.is_listening else "Waiting for wake word"
            status_label.config(text=f"Status: {status}")

            if self.timer_end_time:
                remaining_time = self.timer_end_time - datetime.now()
                if remaining_time.total_seconds() > 0:
                    hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    timer_text = f"Timer: {hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    timer_text = "Timer finished!"
            else:
                timer_text = "No active timer"
            
            timer_label.config(text=timer_text)
            root.after(1000, update_gui)

        update_gui()
        root.mainloop()

def main():
    assistant = VoiceAssistant()
    threading.Thread(target=assistant.listen_for_wake_word, daemon=True).start()
    assistant.run_gui()

if __name__ == "__main__":
    main()