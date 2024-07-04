import speech_recognition as sr
import pyttsx3
import threading
import tkinter as tk
from datetime import datetime

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.wake_word = "taro"
        self.is_listening = False

    def listen_for_wake_word(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=1)
                    text = self.recognizer.recognize_google(audio).lower()
                    if self.wake_word in text:
                        self.is_listening = True
                        self.speak("Yes, I'm listening.")
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

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def run_gui(self):
        root = tk.Tk()
        root.title("Taro Voice Assistant")
        root.geometry("300x100")

        status_label = tk.Label(root, text="Status: Waiting for wake word")
        status_label.pack(pady=20)

        def update_status():
            status = "Listening" if self.is_listening else "Waiting for wake word"
            status_label.config(text=f"Status: {status}")
            root.after(100, update_status)

        update_status()
        root.mainloop()

def main():
    assistant = VoiceAssistant()
    threading.Thread(target=assistant.listen_for_wake_word, daemon=True).start()
    assistant.run_gui()

if __name__ == "__main__":
    main()