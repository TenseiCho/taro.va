# Taro Voice Assistant

Taro is a Python-based voice assistant with a graphical user interface. It can perform various tasks such as telling the time, setting timers, and managing alarms.

## Features

- Wake word detection ("taro")
- Voice command processing
- Current time announcement
- Timer functionality
- Alarm functionality
- Graphical user interface

## Prerequisites

- Python 3.6+
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/taro-voice-assistant.git
   cd taro-voice-assistant
   ```

2. Install the required dependencies:
   ```
   pip install SpeechRecognition pyttsx3 pyaudio pygame pytz
   ```

   Note: If you encounter issues installing PyAudio, you may need to install additional system dependencies. Refer to the PyAudio documentation for your specific operating system.

## Usage

Run the main script:

```
python taro.py
```

Once the GUI appears, you can interact with Taro using voice commands. The assistant will respond accordingly and update the GUI in real-time.

## Known Issues

- Any noise/sound will start the prompt.
- When asked for the time, it doesn't give the time.