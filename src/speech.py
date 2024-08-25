import speech_recognition as sr
import google.generativeai as genai
from gtts  import gTTS
from dotenv import load_dotenv
import os

GOOGLE_API_KEY=os.environ.get("GOOGLE_API_KEY")

def voice():
    src=sr.Recognizer()

    with  sr.Microphone() as source:
        print("Listening ...")
        audio=src.listen(source)
    try:
        text=src.recognize_google(audio)
        print("You said",text)
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand you")
    except  sr.RequestError as e:
        print("Could not request results; {0}".format(e))

def llm(user_text):
    genai.configure(api_key=GOOGLE_API_KEY)
    model=genai.GenerativeModel("gemini-pro")
    response=model.generate_content(user_text)
    result=response.text
    return result

def  text_to_speech(text):
    tts=gTTS(text=text,lang='en')
    tts.save("voice.mp3")



