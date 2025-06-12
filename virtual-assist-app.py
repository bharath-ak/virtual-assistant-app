import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io

st.title("🎙️ Voice Assistant (Cloud Friendly)")

# Get audio from mic
try:
    audio_input = st.audio_input("🎧 Record your voice")
except AttributeError:
    audio_input = st.experimental_audio_input("🎧 Record your voice")

if audio_input:
    st.audio(audio_input, format="audio/wav")
    audio_io = io.BytesIO(audio_input.getvalue())
    audio_io.seek(0)

    # Speech Recognition
    r = sr.Recognizer()
    with sr.AudioFile(audio_io) as source:
        audio_data = r.record(source)

    try:
        text = r.recognize_google(audio_data)
        st.success("🗣️ Recognized Text:")
        st.write(f"**{text}**")

        # Convert text to speech using gTTS
        tts = gTTS(text)
        tts_io = io.BytesIO()
        tts.write_to_fp(tts_io)
        tts_io.seek(0)

        st.success("🔊 Speaking...")
        st.audio(tts_io, format="audio/mp3")

    except sr.UnknownValueError:
        st.error("Sorry, I couldn't understand that.")
    except sr.RequestError as e:
        st.error(f"Google Speech API error: {e}")
