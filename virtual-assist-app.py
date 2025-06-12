import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
from datetime import datetime

st.set_page_config(page_title="Groot: Voice Assistant", page_icon="🌱")

st.title("🌱 Groot: Voice Assistant")

r = sr.Recognizer()
hour = datetime.now().hour
minute = datetime.now().minute

def greet():
    if 5 < hour < 12:
        return 'Good Morning'
    elif 12 <= hour < 17:
        return 'Good Afternoon'
    elif 17 <= hour <= 22:
        return 'Good Evening'
    else:
        return 'Hi'

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

        if 'groot' in instruction or 'greet' in instruction or 'wake up' in instruction:
            response = greet() + ', How may I help you?'
        elif 'how are you' in instruction:
            response = "I'm Groot! I'm doing great."
        elif 'your name' in instruction:
            response = 'I am Groot, your virtual assistant.'
        elif 'what is the time' in instruction or 'time now' in instruction:
            current_time = datetime.now().strftime('%I:%M %p')
            response = 'The time is ' + current_time
        elif 'what is the date' in instruction or "today's date" in instruction:
            current_date = datetime.now().strftime('%B %d, %Y')
            response = "Today's date is " + current_date
        elif 'what day is it' in instruction or 'what day' in instruction or 'day today' in instruction:
            current_day = datetime.now().strftime('%A')
            response = 'Today is ' + current_day
        elif 'play' in instruction:
            song = instruction.replace('play', '').strip()
            link = f"https://www.youtube.com/results?search_query={'+'.join(song.split())}"
            response = f"Here’s a link to play {song} on YouTube: {link}"
        elif 'open' in instruction:
            site = instruction.replace('open','').strip()
            if '.' not in site:
                site += '.com'  
            url = f"https://{site}"
            response = f"Here’s a link to open the site: {url}"
        else:
            response = f"{instruction}"

        st.session_state.history.append(f"🌱 Groot: {response}")
        audio_output = talk(response)
        st.audio(audio_output, format="audio/mp3")

with st.expander("🗒️ Conversation History", expanded=True):
    for line in st.session_state.history:
        st.markdown(line)
