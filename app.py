import streamlit as st
import streamlit.components.v1 as components
from src.speech import upload_audio, llm, text_to_speech
import os
import multiprocessing
from flask import Flask, request, jsonify

def microphone_access_component():
    return """
    <html>
    <head>
        <script>
            let mediaRecorder;
            let audioChunks = [];
            
            function startRecording() {
                navigator.mediaDevices.getUserMedia({ audio: true })
                    .then(stream => {
                        mediaRecorder = new MediaRecorder(stream);
                        mediaRecorder.ondataavailable = event => {
                            audioChunks.push(event.data);
                        };
                        mediaRecorder.onstop = () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            const formData = new FormData();
                            formData.append('audio', audioBlob, 'audio.wav');

                            fetch('/upload_audio', {
                                method: 'POST',
                                body: formData
                            })
                            .then(response => response.json())
                            .then(data => console.log('Audio data sent successfully:', data))
                            .catch(error => console.error('Error sending audio data:', error));
                        };
                        mediaRecorder.start();
                        console.log("Recording started...");
                    })
                    .catch(err => console.error('Microphone access denied:', err));
            }

            function stopRecording() {
                if (mediaRecorder) {
                    mediaRecorder.stop();
                    console.log("Recording stopped...");
                }
            }

            function startAudioRecording() {
                startRecording();
                setTimeout(stopRecording, 5000); // Adjust recording duration as needed
            }

            window.addEventListener('message', (event) => {
                if (event.data === 'startRecording') {
                    startAudioRecording();
                }
            });
        </script>
    </head>
    </html>
    """
def microphone_access():                               
    return """
    <html>
    <head>
        <script>
            function requestMicrophoneAccess() {
                navigator.mediaDevices.getUserMedia({ audio: true })
                    .then(function(stream) {
                        // Successfully received access
                        document.getElementById("microphone-status").innerText = "Microphone access granted.";
                    })
                    .catch(function(err) {
                        // Failed to receive access
                        document.getElementById("microphone-status").innerText = "Microphone access denied.";
                    });
            }

            // Automatically request microphone access when the page loads
            window.onload = function() {
                requestMicrophoneAccess();
            };
        </script>
    </head>
    <body>
        <h2>Microphone Access</h2>
        <p id="microphone-status">Requesting microphone access...</p>
    </body>
    </html>
    """

def start_flask():
    if not hasattr(st, 'already_started_server'):
        st.already_started_server = True
        must_reload_page = True
        app = Flask(__name__)

        @app.route('/upload_audio', methods=['POST'])
        def upload_audio():
            try:
                audio_file = request.files['audio']
                audio_file.save('uploaded_audio.wav')
                return jsonify({'message': 'File uploaded successfully'}), 200
            except KeyError:
                return jsonify({'error': 'No audio file uploaded'}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        app.run(port=8888)

def reload_page():
    if must_reload_page:
        must_reload_page = False
        st.experimental_rerun()


def main():
    st.title("Multilingual AI Assistant")

    with st.sidebar:
        GOOGLE_API_KEY = st.text_input("Enter your GOOGLE_API_KEY:")
        if st.button("Enter"):
            os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
            st.session_state.api_key_provided = True
            components.html(microphone_access(),height=300)
           

    if 'api_key_provided' in st.session_state and st.session_state.api_key_provided:
        # Include the microphone access component
       
  
        if st.button("Click to start"):
            components.html(microphone_access_component(), height=0)
            st.components.v1.html(f"""
            <script>
                window.postMessage('startRecording', '*');
                console.log("processing starts");
            </script>
            """, height=0)
            
            with st.spinner("Listening"): 
                audio = upload_audio()
                text = llm(audio)
                speech = text_to_speech(text)

                audio_file = open("voice.mp3", "rb")
                audio_bytes = audio_file.read()

                st.text_area(label="Response", value=text, height=350)
                st.audio(audio_bytes)
                st.download_button(label="Download Speech", data=audio_bytes, file_name='voice.mp3', mime="audio/mp3")

if __name__ == "__main__":
    must_reload_page = False
    flask_process = multiprocessing.Process(target=start_flask)
    reload_process = multiprocessing.Process(target=reload_page)
    flask_process.start()
    reload_process.start()
    main()
