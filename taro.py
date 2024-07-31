import speech_recognition as sr
import pyttsx3
import threading
import tkinter as tk
from datetime import datetime, timedelta
import pygame
import re
import time
import pytz
import pyaudio

# Constants
WAKE_WORD = "taro"
TIMEZONE = 'US/Eastern'
WAKE_SOUND_FILE = "start.wav"
TIMER_SOUND_FILE = "gameover.wav"

class Timer:
    """Represents a countdown timer."""

    def __init__(self, duration: int, callback: callable):
        self.duration = duration
        self.end_time: datetime = None
        self.callback = callback
        self.thread: threading.Timer = None

    def start(self):
        self.end_time = datetime.now() + timedelta(seconds=self.duration)
        self.thread = threading.Timer(self.duration, self.callback)
        self.thread.start()

    def cancel(self):
        if self.thread and self.thread.is_alive():
            self.thread.cancel()
            self.end_time = None

    def get_remaining_time(self):
        if self.end_time:
            remaining = self.end_time - datetime.now()
            return max(timedelta(0), remaining)
        return None

class Alarm:
    """Represents an alarm clock."""

    def __init__(self, alarm_time: datetime, callback: callable):
        self.alarm_time = alarm_time
        self.callback = callback
        self.thread: threading.Timer = None
        self.is_ringing = False

    def start(self):
        now = datetime.now(pytz.timezone(TIMEZONE))
        time_until_alarm = (self.alarm_time - now).total_seconds()
        self.thread = threading.Timer(time_until_alarm, self.trigger)
        self.thread.start()

    def cancel(self):
        if self.thread and self.thread.is_alive():
            self.thread.cancel()
        self.is_ringing = False

    def trigger(self):
        self.is_ringing = True
        self.callback()

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen_for_wake_word(self, wake_word, callback):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=1)
                    text = self.recognizer.recognize_google(audio).lower()
                    if wake_word in text:
                        callback()
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    pass
                except sr.RequestError:
                    print("Could not request results from speech recognition service")

    def listen_for_command(self, timeout=5, phrase_time_limit=5):
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            try:
                return self.recognizer.recognize_google(audio).lower()
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                return None

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

class SoundPlayer:
    def __init__(self, wake_sound_file, timer_sound_file):
        pygame.mixer.init()
        self.wake_sound = pygame.mixer.Sound(wake_sound_file)
        self.timer_sound = pygame.mixer.Sound(timer_sound_file)

    def play_wake_sound(self):
        pygame.mixer.Sound.play(self.wake_sound)

    def play_timer_sound(self):
        pygame.mixer.Sound.play(self.timer_sound)

class CommandProcessor:
    def __init__(self, voice_assistant):
        self.voice_assistant = voice_assistant

    def process_command(self, command):
        if "set timer" in command or "start timer" in command:
            self.set_timer(command)
        elif "cancel timer" in command:
            self.voice_assistant.cancel_timer()
        elif "set alarm" in command:
            self.set_alarm(command)
        elif "cancel alarm" in command:
            self.voice_assistant.cancel_alarm()
        elif "what time" in command or "current time" in command:
            self.tell_time()
        else:
            self.voice_assistant.speak(f"You said: {command}")

    def set_timer(self, command):
        minutes = 0
        hours = 0
        
        minute_match = re.search(r'(\d+)\s*minute', command)
        hour_match = re.search(r'(\d+)\s*hour', command)
        
        if minute_match:
            minutes = int(minute_match.group(1))
        if hour_match:
            hours = int(hour_match.group(1))
        
        if minutes == 0 and hours == 0:
            self.voice_assistant.speak("I'm sorry, I couldn't understand the timer duration. Please try again.")
            return
        
        total_seconds = minutes * 60 + hours * 3600
        
        timer_message = []
        if hours > 0:
            timer_message.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            timer_message.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        
        timer_str = " and ".join(timer_message)
        self.voice_assistant.speak(f"Timer set for {timer_str}.")
        
        self.voice_assistant.set_timer(total_seconds)

    def set_alarm(self, command):
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', command)
        if time_match:
            hours, minutes, meridiem = time_match.groups()
            hours = int(hours)
            minutes = int(minutes)
            
            if meridiem:
                if meridiem.lower() == 'pm' and hours != 12:
                    hours += 12
                elif meridiem.lower() == 'am' and hours == 12:
                    hours = 0
            
            now = datetime.now(self.voice_assistant.est_tz)
            alarm_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            
            if alarm_time <= now:
                alarm_time += timedelta(days=1)
            
            self.voice_assistant.speak(f"Alarm set for {alarm_time.strftime('%I:%M %p')} Eastern Standard Time.")
            self.voice_assistant.set_alarm(alarm_time)
        else:
            self.voice_assistant.speak("I'm sorry, I couldn't understand the alarm time. Please try again.")

    def tell_time(self):
        current_time = datetime.now(self.voice_assistant.est_tz).strftime("%I:%M %p")
        self.voice_assistant.speak(f"The current time is {current_time}")

class VoiceAssistant:
    """Main class for the voice assistant."""

    def __init__(self):
        self.speech_recognizer = SpeechRecognizer()
        self.text_to_speech = TextToSpeech()
        self.sound_player = SoundPlayer(WAKE_SOUND_FILE, TIMER_SOUND_FILE)
        self.command_processor = CommandProcessor(self)
        self.is_listening = False
        self.est_tz = pytz.timezone(TIMEZONE)
        self.pa = pyaudio.PyAudio()
        self.timer: Timer = None
        self.alarm: Alarm = None

    def listen_for_wake_word(self):
        self.speech_recognizer.listen_for_wake_word(WAKE_WORD, self.wake_word_detected)

    def wake_word_detected(self):
        self.is_listening = True
        self.sound_player.play_wake_sound()
        self.process_command()

    def process_command(self):
        command = self.speech_recognizer.listen_for_command()
        if command:
            self.command_processor.process_command(command)
        else:
            self.speak("Sorry, I didn't understand that.")
        self.is_listening = False

    def speak(self, text):
        self.text_to_speech.speak(text)

    def set_timer(self, duration):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(duration, self.timer_finished)
        self.timer.start()

    def cancel_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None
            self.speak("Timer cancelled.")
        else:
            self.speak("There is no active timer to cancel.")

    def timer_finished(self):
        self.sound_player.play_timer_sound()
        self.timer = None

    def set_alarm(self, alarm_time):
        if self.alarm:
            self.alarm.cancel()
        self.alarm = Alarm(alarm_time, self.alarm_triggered)
        self.alarm.start()

    def cancel_alarm(self):
        if self.alarm:
            self.alarm.cancel()
            self.alarm = None
            self.speak("Alarm cancelled.")
        else:
            self.speak("There is no active alarm to cancel.")

    def alarm_triggered(self):
        while self.alarm and self.alarm.is_ringing:
            self.sound_player.play_timer_sound()
            time.sleep(1)
        self.alarm = None

    def run_gui(self):
        """Run the graphical user interface."""
        root = tk.Tk()
        root.title("Taro Voice Assistant")
        root.geometry("300x250")

        status_label = tk.Label(root, text="Status: Waiting for wake word")
        status_label.pack(pady=10)

        timer_label = tk.Label(root, text="No active timer")
        timer_label.pack(pady=10)

        alarm_label = tk.Label(root, text="No active alarm")
        alarm_label.pack(pady=10)

        cancel_alarm_button = tk.Button(root, text="Cancel Alarm", command=self.cancel_alarm)

        def update_gui():
            self.update_status_label(status_label)
            self.update_timer_label(timer_label)
            self.update_alarm_label(alarm_label, cancel_alarm_button)
            root.after(1000, update_gui)  # Update every second

        update_gui()
        root.mainloop()

    def update_status_label(self, label: tk.Label):
        """Update the status label in the GUI."""
        status = "Listening" if self.is_listening else "Waiting for wake word"
        label.config(text=f"Status: {status}")

    def update_timer_label(self, label: tk.Label):
        """Update the timer label in the GUI."""
        if self.timer:
            remaining_time = self.timer.get_remaining_time()
            if remaining_time:
                timer_text = f"Timer: {str(remaining_time).split('.')[0]}"
            else:
                timer_text = "Timer finished!"
        else:
            timer_text = "No active timer"
        label.config(text=timer_text)

    def update_alarm_label(self, label: tk.Label, button: tk.Button):
        """Update the alarm label and button in the GUI."""
        if self.alarm:
            alarm_text = f"Alarm: {self.alarm.alarm_time.strftime('%I:%M %p')} EST"
            if self.alarm.is_ringing:
                alarm_text += " (Ringing!)"
                button.pack(pady=10)
            else:
                button.pack_forget()
        else:
            alarm_text = "No active alarm"
            button.pack_forget()
        label.config(text=alarm_text)

def main():
    assistant = VoiceAssistant()
    threading.Thread(target=assistant.listen_for_wake_word, daemon=True).start()
    assistant.run_gui()

if __name__ == "__main__":
    main()