import streamlit as st

st.title("Mic Test")

try:
    audio_bytes = st.audio_input("Tap to record") 
except AttributeError:
    audio_bytes = st.experimental_audio_input("Tap to record")

if audio_bytes:
    st.audio(audio_bytes)
    st.write("Got your recording!")
