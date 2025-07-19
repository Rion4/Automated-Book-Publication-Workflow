import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os

AUDIO_FILE = "temp_audio.mp3"

def speak(text: str):
  
    if not text or text.isspace():
        print("Speak function received empty text. Nothing to say.")
        return
        
    try:
        print("Generating speech...")
        tts = gTTS(text=text, lang='en', slow=False)
        
        tts.save(AUDIO_FILE)
        
        print(f"Speaking: '{text[:60]}...'")
        playsound(AUDIO_FILE)
        
    except Exception as e:
        print(f"An error occurred during text-to-speech: {e}")
    finally:
        if os.path.exists(AUDIO_FILE):
            os.remove(AUDIO_FILE)

def listen_for_input(prompt: str) -> str:
   
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Calibrating for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=1)
        
        print(prompt)
        speak(prompt) 
        
        try:
            # Listen for audio input from the user.
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
            
            print("Recognizing speech...")
            # Use Google's speech recognition engine to transcribe the audio.
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("Listening timed out. No speech detected.")
            return ""
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio.")
            speak("Sorry, I didn't catch that. Please try again.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            speak("Sorry, my speech service is currently down.")
            return ""
        except Exception as e:
            print(f"An unknown error occurred during listening: {e}")
            return ""