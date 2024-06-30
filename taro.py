import speech_recognition as sr
import pyttsx3
import time

def play_sound(sound_type):
    # Placeholder function for playing sounds
    # Replace this with actual sound playing code
    print(f"Playing {sound_type} sound")

def listen_for_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for 'Taro'...")
        audio = r.listen(source)
    
    try:
        text = r.recognize_google(audio).lower()
        if "taro" in text:
            return True
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print("Could not request results from the speech recognition service")
    
    return False

def get_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        play_sound("start_listening")
        print("Listening for command...")
        try:
            audio = r.listen(source, timeout=8, phrase_time_limit=8)
            play_sound("stop_listening")
            text = r.recognize_google(audio).lower()
            return text
        except sr.WaitTimeoutError:
            play_sound("stop_listening")
            print("No command detected")
        except sr.UnknownValueError:
            play_sound("stop_listening")
            print("Could not understand audio")
        except sr.RequestError:
            play_sound("stop_listening")
            print("Could not request results from the speech recognition service")
    
    return None

def respond(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    while True:
        if listen_for_command():
            command = get_command()
            if command:
                print(f"Command received: {command}")
                # Here you would process the command and generate a response
                response = f"You said: {command}"
                respond(response)
        time.sleep(1)  # Small delay to prevent excessive CPU usage

if __name__ == "__main__":
    main()