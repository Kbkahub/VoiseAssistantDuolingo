import streamlit as st
from googletrans import Translator
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO

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

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Record audio input
st.write("Press the button below and speak in English:")
if st.button("Start Recording"):
    with sr.Microphone() as source:
        st.write("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            st.write("Processing...")
            english_text = recognizer.recognize_google(audio)
            st.write(f"Recognized Text (English): {english_text}")
        except sr.UnknownValueError:
            st.error("Sorry, could not understand the audio.")
        except sr.RequestError:
            st.error("Error in the speech recognition service.")

        if 'english_text' in locals():
            # Translate to target language
            target_lang_code = languages[selected_language]
            translation = translator.translate(english_text, src="en", dest=target_lang_code)
            translated_text = translation.text
            st.write(f"Translated Text ({selected_language}): {translated_text}")

            if show_explanation:
                st.write(f"Explanation: {translation.extra_data}")

            # Convert translated text to speech
            tts = gTTS(text=translated_text, lang=target_lang_code)
            audio_data = BytesIO()
            tts.write_to_fp(audio_data)
            audio_data.seek(0)  # Rewind the buffer to the beginning

            # Play the audio directly in Streamlit
            st.audio(audio_data, format="audio/mp3")
