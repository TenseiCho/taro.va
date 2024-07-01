import speech_recognition as sr
import pyttsx3
import time
from datetime import datetime
from playsound import playsound
import os

def play_sound(sound_type):
    sound_file = os.path.join("sounds", f"{sound_type}")
    try:
        playsound(sound_file)
    except Exception as e:
        print(f"Error playing sound {sound_file}: {e}")

def listen_for_command():
    r = sr.Recognizer()
    r.energy_threshold = 4000  # Increase the energy threshold
    r.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        print("Listening for 'Taro'...")
        r.adjust_for_ambient_noise(source, duration=2)
        try:
            print("Say something...")
            audio = r.listen(source, timeout=10, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Listening timed out. Please try again.")
            return False
    
    try:
        print("Recognizing...")
        # Try Google Speech Recognition first
        try:
            text = r.recognize_google(audio).lower()
        except:
            # If Google fails, fall back to Sphinx
            text = r.recognize_sphinx(audio).lower()
        print(f"Recognized: {text}")
        if "taro" in text:
            play_sound("start.m4a")
            return True
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from the speech recognition service; {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return False

def get_command():
    r = sr.Recognizer()
    r.energy_threshold = 4000  # Increase the energy threshold
    r.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        play_sound("start.m4a")
        print("Listening for command...")
        r.adjust_for_ambient_noise(source, duration=2)
        try:
            print("Say your command...")
            audio = r.listen(source, timeout=10, phrase_time_limit=8)
            play_sound("stop.opus")
        except sr.WaitTimeoutError:
            play_sound("stop.opus")
            print("Listening timed out. No command detected.")
            return None
    
    try:
        print("Recognizing command...")
        # Try Google Speech Recognition first
        try:
            text = r.recognize_google(audio).lower()
        except:
            # If Google fails, fall back to Sphinx
            text = r.recognize_sphinx(audio).lower()
        print(f"Recognized command: {text}")
        return text
    except sr.UnknownValueError:
        play_sound("stop.opus")
        print("Could not understand audio")
    except sr.RequestError as e:
        play_sound("stop.opus")
        print(f"Could not request results from the speech recognition service; {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return None

# The rest of the code remains the same
def respond(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    return f"The current time is {current_time}"

def process_command(command):
    if "what time is it" in command:
        return get_current_time()
    else:
        return f"You said: {command}"

def main():
    while True:
        if listen_for_command():
            command = get_command()
            if command:
                print(f"Command received: {command}")
                response = process_command(command)
                respond(response)
        time.sleep(1)  # Small delay to prevent excessive CPU usage

if __name__ == "__main__":
    main()