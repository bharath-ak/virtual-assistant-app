import streamlit as st

st.title("Mic Record & Play")

try:
    audio_bytes = st.audio_input("Tap to record (keep it short)")
except AttributeError:
    audio_bytes = st.experimental_audio_input("Tap to record (keep it short)")

if audio_bytes:
    st.write(f"Received {len(audio_bytes)} bytes")
    try:
        st.audio(audio_bytes, format="audio/wav")
    except Exception as err:
        st.error(f"Playback error: {err}")
