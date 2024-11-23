import streamlit as st
from googletrans import Translator
from gtts import gTTS
import sounddevice as sd
import numpy as np
from io import BytesIO
import wave

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

# Function to record audio
def record_audio(duration=5, samplerate=44100):
    st.write("Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    st.write("Recording complete.")
    return audio, samplerate

# Function to save audio to memory (BytesIO buffer)
def save_audio_to_buffer(audio, samplerate):
    buffer = BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)  # Mono channel
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())
    buffer.seek(0)
    return buffer

# Main app logic
if st.button("Record and Translate"):
    # Record audio
    duration = st.slider("Recording duration (seconds):", min_value=1, max_value=10, value=5)
    audio, samplerate = record_audio(duration)

    # Convert audio to text (placeholder for actual STT implementation)
    # Here, simulate recognized text for demo purposes:
    english_text = st.text_input("Simulated recognized text (enter your text here):", "Hello, how are you?")
    
    if english_text:
        # Translate to target language
        target_lang_code = languages[selected_language]
        translation = translator.translate(english_text, src="en", dest=target_lang_code)
        translated_text = translation.text
        st.write(f"Translated Text ({selected_language}): {translated_text}")

        if show_explanation:
            st.write(f"Explanation: {translation.extra_data}")  # Shows extra translation data

        # Convert translated text to speech
        tts = gTTS(text=translated_text, lang=target_lang_code)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        # Play the translated audio
        st.audio(audio_buffer, format="audio/mp3")
