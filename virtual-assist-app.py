import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
import wikipedia
import smtplib
import requests
from datetime import datetime
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
import time
import re

st.set_page_config(page_title="Groot: Voice Assistant", page_icon="🌱")

st.title("🌱 Groot: Voice Assistant")

local_now = datetime.now().astimezone()
st.write(time.timezone)
st.write(time.tzname)

r = sr.Recognizer()
API_KEY = st.secrets["ipdata"]["api_key"]
url = f"https://api.ipdata.co?api-key={API_KEY}"
location = requests.get(url).json()
latitude = location.get("latitude")
longitude = location.get("longitude")
tf = TimezoneFinder()
tz_name = tf.timezone_at(lat=latitude, lng=longitude)

local_time = datetime.now(ZoneInfo(tz_name))
hour = local_time.hour
minute = local_time.minute

if 'history' not in st.session_state:
    st.session_state.history = []

def talk(text):
    tts = gTTS(text)
    tts_io = io.BytesIO()
    tts.write_to_fp(tts_io)
    tts_io.seek(0)
    return tts_io

def greet():
    if 5 < hour < 12:
        return 'Good Morning'
    elif 12 <= hour < 17:
        return 'Good Afternoon'
    elif 17 <= hour <= 22:
        return 'Good Evening'
    else:
        return 'Hi'

def search_wikipedia(instruction):
    try:
        instruction = instruction.lower()
        topic = ''

        for phrase in ['tell me about', 'who is', 'what is']:
            if phrase in instruction:
                topic = instruction.replace(phrase, '').strip()
                break

        if topic:
            page = wikipedia.page(topic, auto_suggest=False)
            summary = wikipedia.summary(topic, sentences=2)
            page_url = page.url
            return summary, page_url
        else:
            return 'Please specify a topic to search on Wikipedia.', None

    except wikipedia.exceptions.DisambiguationError as e:
        return 'There are multiple results for that. Please be more specific.', None

    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find any results on Wikipedia.", None

    except Exception as e:
        return 'Something went wrong while searching Wikipedia.', None
        print('Error:', e)

    return response

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
        elif 'how are you' in instruction or "how's it going" in instruction or "what's up" in instruction:
            response = "I'm Groot! I'm doing great."
        elif 'your name' in instruction:
            response = 'I am Groot, your virtual assistant.'
        elif 'what is the time' in instruction or 'time now' in instruction:
            current_time = local_time.strftime('%I:%M %p')
            response = 'The time is ' + current_time
        elif 'what is the date' in instruction or "today's date" in instruction:
            current_date = local_time.strftime('%B %d, %Y')
            response = "Today's date is " + current_date
        elif 'what day is it' in instruction or 'what day' in instruction or 'day today' in instruction:
            current_day = local_time.strftime('%A')
            response = 'Today is ' + current_day
        elif 'play' in instruction:
            song = instruction.replace('play', '').strip()
            link = f"https://www.youtube.com/results?search_query={'+'.join(song.split())}"
            # pywhatkit.playonyt(song)
            response = f"Here’s a link to play {song} on YouTube: {link}"
        elif 'open' in instruction:
            site = instruction.replace('open','').strip()
            if '.' not in site:
                site += '.com'
            url = f"https://{site}"
            # webbrowser.open(url)
            response = f"Here’s a link to open the site: {url}"
        elif 'tell me about' in instruction or 'who is' in instruction or 'what is' in instruction:
            response, wiki_url = search_wikipedia(instruction)
            if wiki_url:
                st.link_button("🔗 Read more on Wikipedia", url=wiki_url)            
        elif 'send whatsapp message' in instruction:
            match = re.search(r"send whatsapp message to (\d+) as ([a-zA-Z\s]*)", instruction)
            phone_no = match.group(1)
            msg = match.group(2)
            # pywhatkit.sendwhatmsg(phone_no, msg, hour, minute)    
            response = f"Message sent to {phone_no} at {hour} and {minute}."
        elif 'send email' in instruction:
            send_email()
        elif 'exit' in instruction or 'quit' in instruction or 'bye' in instruction:
            response = "Goodbye! See you later."
        else:
            response = f"{instruction}"

        st.session_state.history.append(f"🌱 Groot: {response}")
        audio_output = talk(response)
        st.audio(audio_output, format="audio/mp3")

with st.expander("🗒️ Conversation History", expanded=True):
    for line in st.session_state.history:
        st.markdown(line)
