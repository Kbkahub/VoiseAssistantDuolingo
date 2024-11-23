import streamlit as st
from googletrans import Translator
from gtts import gTTS
from io import BytesIO
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode, ClientSettings
import numpy as np
import av
import asyncio

# Initialize Translator
translator = Translator()

# Set up Streamlit interface
st.title("Multilingual Voice Assistant for Language Learning")

# Language options
languages = {
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-cn",
    "Japanese": "ja",
    "Hindi": "hi",
    "Arabic": "ar"
}
selected_language = st.selectbox("Select the language you want to learn:", list(languages.keys()))
show_explanation = st.checkbox("Show translation explanation")

# Function to process audio and perform speech-to-text
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_frames = []
        self.result_text = ""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convert the frame to numpy array
        audio = frame.to_ndarray()

        # Append audio data
        self.audio_frames.append(audio)

        return frame

# Function to convert audio frames to audio buffer
def audio_frames_to_bytes(audio_frames):
    audio_np = np.concatenate(audio_frames)
    audio_bytes = audio_np.tobytes()
    return audio_bytes

# Main app logic
def main():
    st.write("Press 'Start' to begin recording and 'Stop' when you are done.")

    # WebRTC Streamer
    ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDRECV,
        client_settings=ClientSettings(
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"audio": True, "video": False},
        ),
        audio_processor_factory=AudioProcessor,
        async_processing=True,
    )

    if ctx.state.playing:
        if st.button("Process Audio"):
            if ctx.audio_processor:
                audio_processor = ctx.audio_processor
                # Wait for audio frames to be collected
                st.info("Processing audio...")
                # Allow some time for audio to be processed
                asyncio.run(asyncio.sleep(1))
                audio_frames = audio_processor.audio_frames
                if audio_frames:
                    # Convert audio frames to bytes
                    audio_bytes = audio_frames_to_bytes(audio_frames)

                    # Save audio bytes to a BytesIO buffer
                    audio_buffer = BytesIO(audio_bytes)

                    # Perform speech-to-text using a service (e.g., Google Speech Recognition)
                    import speech_recognition as sr
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(audio_buffer) as source:
                        audio_data = recognizer.record(source)
                        try:
                            english_text = recognizer.recognize_google(audio_data)
                            st.write(f"Recognized Text (English): {english_text}")

                            # Translate to target language
                            target_lang_code = languages[selected_language]
                            translation = translator.translate(english_text, src="en", dest=target_lang_code)
                            translated_text = translation.text
                            st.write(f"Translated Text ({selected_language}): {translated_text}")

                            if show_explanation:
                                st.write(f"Explanation: {translation.extra_data}")  # Shows extra translation data

                            # Convert translated text to speech
                            tts = gTTS(text=translated_text, lang=target_lang_code)
                            tts_buffer = BytesIO()
                            tts.write_to_fp(tts_buffer)
                            tts_buffer.seek(0)

                            # Play the translated audio
                            st.audio(tts_buffer, format="audio/mp3")

                        except sr.UnknownValueError:
                            st.error("Could not understand the audio.")
                        except sr.RequestError as e:
                            st.error(f"Could not request results from the speech recognition service; {e}")
                else:
                    st.warning("No audio frames received.")
            else:
                st.warning("Audio processor not initialized.")
    else:
        st.write("Click the 'Start' button to begin.")

if __name__ == "__main__":
    main()
