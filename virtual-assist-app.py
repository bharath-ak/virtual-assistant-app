import streamlit as st
import speech_recognition as sr
import io

st.title("🎙️ Streamlit Voice Assistant")

# Use correct audio input method
try:
    audio_input = st.audio_input("Tap to record your voice...")
except AttributeError:
    audio_input = st.experimental_audio_input("Tap to record your voice...")

if audio_input:
    # Ensure the file pointer is reset
    audio_io = io.BytesIO(audio_input.getvalue())
    audio_io.seek(0)

    # Playback
    st.audio(audio_io, format="audio/wav")
    st.success(f"Received {len(audio_io.getvalue())} bytes")

    # Recognize speech
    r = sr.Recognizer()
    with sr.AudioFile(audio_io) as source:
        audio_data = r.record(source)

    try:
        text = r.recognize_google(audio_data)
        st.success("🗣️ Recognized Text:")
        st.markdown(f"**{text}**")
    except sr.UnknownValueError:
        st.error("Sorry, I couldn't understand the audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service: {e}")
