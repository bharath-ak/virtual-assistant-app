import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
import wikipedia
import smtplib
import requests
from datetime import datetime
import time
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh
import re

st.set_page_config(page_title="Groot: Voice Assistant", page_icon="🌱")

st.title("🌱 Groot: Voice Assistant")

r = sr.Recognizer()

now = datetime.now(ZoneInfo('Asia/Kolkata'))
hour = now.hour
minute = now.minute

if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_instruction' not in st.session_state:
    st.session_state.last_instruction = ''
if 'reminder_set' not in st.session_state:
    st.session_state.reminder_set = False
if 'reminder_triggered' not in st.session_state:
    st.session_state.reminder_triggered = False
if 'reminder_time' not in st.session_state:
    st.session_state.reminder_time = 0
if 'reminder_task' not in st.session_state:
    st.session_state.reminder_task = ''

if st.session_state.reminder_set and not st.session_state.reminder_triggered:
    st_autorefresh(interval=1000, limit=None)

def talk(text):
    tts = gTTS(text)
    tts_io = io.BytesIO()
    tts.write_to_fp(tts_io)
    tts_io.seek(0)
    return tts_io

def greet(hour):
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

def set_reminder(instruction):
    try:
        match = re.search(r"remind me to (.+) in (\d+)\s*(seconds?|minutes?|hours?)", instruction.lower())
        if not match:
            return "I didn't understand the reminder format. Please say something like 'remind me to take medicine in 10 minutes'."

        task = match.group(1).strip()
        delay_time = int(match.group(2))
        unit = match.group(3).lower()

        seconds = delay_time
        if 'minute' in unit:
            seconds *= 60
        elif 'hour' in unit:
            seconds *= 3600
            
        st.session_state.reminder_set = True
        st.session_state.reminder_triggered = False
        st.session_state.reminder_task = task
        st.session_state.reminder_time = time.time() + seconds

        # def reminder_task():
            # reminder_text = f"🔔 Reminder: {task}"
            # st.session_state.history.append(f"🌱 Groot: {reminder_text}")
            # audio_output = talk(reminder_text)
            # st.audio(audio_output, format="audio/mp3")

        # threading.Timer(seconds, reminder_task).start()

        return f"✅ Reminder set to '{task}' in {delay_time} {unit}."
    except Exception as e:
        print("Reminder error:", e)
        return "❌ Failed to set reminder. Please try again."

def read_instruction(audio_input):
    try:
        with sr.AudioFile(io.BytesIO(audio_input.getvalue())) as source:
            audio_data = r.record(source)
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

st.write("🔁 Checking reminder status...")
st.write("🔍 reminder_set:", st.session_state.get("reminder_set"))
if st.session_state.get("reminder_set"):
    remaining = int(st.session_state.reminder_time - time.time())
    st.write("DEBUG: Current time =", time.time())
    st.write("DEBUG: Reminder time =", st.session_state.reminder_time)
    st.write("DEBUG: Time remaining =", remaining)
    if remaining > 0:
        st.info(f"⏳ Reminder in: {remaining} second(s)")
    elif not st.session_state.reminder_triggered:
        reminder_text = f"🔔 Reminder: {st.session_state.reminder_task}"
        st.session_state.history.append(f"🌱 Groot: {reminder_text}")
        st.success(reminder_text)
        # st.audio(talk(reminder_text), format="audio/mp3")
        st.session_state.reminder_set = False
        st.session_state.reminder_triggered = True 

if audio_input:
    st.audio(audio_input, format="audio/wav")
    instruction = read_instruction(audio_input)

    if instruction and instruction != st.session_state.last_instruction:
        st.session_state.last_instruction = instruction
        st.session_state.history.append(f"👤 You: {instruction}")
        
        if 'groot' in instruction or 'greet' in instruction or 'wake up' in instruction:
            response = greet(hour) + ', How may I help you?'
        elif 'how are you' in instruction or "how's it going" in instruction or "what's up" in instruction:
            response = "I'm Groot! I'm doing great."
        elif 'your name' in instruction:
            response = 'I am Groot, your virtual assistant.'
        elif 'what is the time' in instruction or 'time now' in instruction:
            current_time = now.strftime('%I:%M %p')
            response = 'The time is ' + current_time
        elif 'what is the date' in instruction or "today's date" in instruction:
            current_date = now.strftime('%B %d, %Y')
            response = "Today's date is " + current_date
        elif 'what day is it' in instruction or 'what day' in instruction or 'day today' in instruction:
            current_day = now.strftime('%A')
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
        elif 'remind me' in instruction or 'set reminder' in instruction:
            response = set_reminder(instruction)
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
        st.audio(talk(response), format="audio/mp3")

with st.expander("🗒️ Conversation History", expanded=True):
    for line in st.session_state.history:
        st.markdown(line)
