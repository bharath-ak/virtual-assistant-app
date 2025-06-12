import streamlit as st

st.title("🎤 Mic Recorder Test")

try:
    audio_bytes = st.audio_input("Record something...")
except AttributeError:
    audio_bytes = st.experimental_audio_input("Record something...")

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    st.write(f"Received {len(audio_bytes.getvalue())} bytes")
