import streamlit as st
from src.speech import voice, llm,  text_to_speech
import os

def main():
    st.title("Multilingual AI Assistant")
    with st.sidebar:
        GOOGLE_API_KEY = st.text_input("Enter your GOOGLE_API_KEY:")
        if st.button("Enter"):
            os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
    if st.button("Click to start"):
        with st.spinner("Listining"):
            audio = voice()
            text=llm(audio)
            speech=text_to_speech(text)

            audio_file=open("voice.mp3","rb")
            audio_bytes=audio_file.read()

            st.text_area(label="Response",value=text,height=350)
            st.audio(audio_bytes)
            st.download_button(label="Download Speech",data=audio_bytes,file_name='voice.mp3',mime="audio/mp3")
    

if __name__=="__main__":
    main()
