import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io

st.set_page_config(page_title="Groot: Voice Assistant", page_icon="🌱")

st.title("🌱 Groot: Voice Assistant")

r = sr.Recognizer()
if 'history' not in st.session_state:
    st.session_state.history = []

def read_instruction(audio_input):
    instruction = ''
    if audio_input:
        audio_io = io.BytesIO(audio_input.getvalue())
        audio_io.seek(0)
        with sr.AudioFile(audio_io) as source:
            audio_data = r.record(source)
        try:
            instruction = r.recognize_google(audio_data).lower()
            return instruction
        except Exception as e:
            st.error("❌ Error recognizing speech.")
            print('Speech recognition error:', e)
    return ''

def talk(text):
    tts = gTTS(text)
    tts_io = io.BytesIO()
    tts.write_to_fp(tts_io)
    tts_io.seek(0)
    return tts_io

try:
    audio_input = st.audio_input("🎧 Tap to record")
except AttributeError:
    audio_input = st.experimental_audio_input("🎧 Tap to record")

if audio_input:
    st.audio(audio_input, format="audio/wav")
    instruction = read_instruction(audio_input)

    if instruction:
        st.session_state.history.append(f"👤 You: {instruction}")

        # Simple response logic (you can customize)
        if "how are you" in instruction:
            response = "I'm Groot! I'm doing great."
        elif "your name" in instruction:
            response = "I am Groot, your virtual assistant."
        elif "time" in instruction:
            from datetime import datetime
            response = f"The current time is {datetime.now().strftime('%I:%M %p')}."
        else:
            response = f"You said: {instruction}"

        st.session_state.history.append(f"🌱 Groot: {response}")
        audio_output = talk(response)
        st.audio(audio_output, format="audio/mp3")

# Chat history
with st.expander("🗒️ Conversation History", expanded=True):
    for line in st.session_state.history:
        st.markdown(line)
