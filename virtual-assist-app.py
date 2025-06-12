import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO

st.title("🎙️ Microphone Speech-to-Text with Streamlit")

st.markdown("Record your voice and I'll transcribe it for you using Google Speech Recognition.")

# Step 1: Record audio using Streamlit's browser interface
audio_bytes = st.audio_input("Tap to record", type="wav")

if audio_bytes:
    st.audio(audio_bytes)  # Optional playback

    # Step 2: Convert to format SpeechRecognition understands
    audio = AudioSegment.from_file(BytesIO(audio_bytes), format="wav")
    audio = audio.set_channels(1).set_frame_rate(16000)  # Mono & 16kHz recommended
    wav_io = BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)

    # Step 3: Transcribe using SpeechRecognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_io) as source:
        audio_data = recognizer.record(source)

    try:
        transcript = recognizer.recognize_google(audio_data)
        st.success("📝 Transcription:")
        st.write(transcript)
    except sr.UnknownValueError:
        st.warning("Google Speech Recognition could not understand audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
