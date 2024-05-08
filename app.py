import streamlit as st
import requests
import os
import google.generativeai as genai
from st_audiorec import st_audiorec

# Set up API keys
DEEPGRAM_STT_ENDPOINT = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
DEEPGRAM_TTS_ENDPOINT = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"

# Configure Google AI
genai.configure(api_key=GOOGLE_API_KEY)

initial_prompt = "*Your job is to teach the user English, become a language partner, give good feedback on the language, and keep the conversation continued. Don't talk more than 30 words in one message*"

# Initialize or retrieve ongoing chat from session state
if 'chat' not in st.session_state:
    model = genai.GenerativeModel('gemini-pro')
    st.session_state.chat = model.start_chat(history=[])
    # Send system prompt to set the conversation context
    st.session_state.chat.send_message(initial_prompt)

def transcribe_audio(audio_data):
    """Transcribe audio data to text using Deepgram API."""
    headers = {'Authorization': f'Token {DEEPGRAM_API_KEY}', 'Content-Type': 'audio/wav'}
    response = requests.post(DEEPGRAM_STT_ENDPOINT, headers=headers, data=audio_data)
    if response.status_code == 200:
        return response.json()['results']['channels'][0]['alternatives'][0]['transcript']
    return "Transcription failed."

def synthesize_speech(text):
    """Convert text to speech using Deepgram API."""
    headers = {'Content-Type': 'application/json', 'Authorization': f'Token {DEEPGRAM_API_KEY}'}
    data = {'text': text}
    response = requests.post(DEEPGRAM_TTS_ENDPOINT, headers=headers, json=data)
    if response.status_code == 200:
        return response.content
    return None

st.title("English Language Coach")

# Play the initial instruction from the model
if 'initial_audio' not in st.session_state:
    initial_response = "I am your english speaking partner. What do you want to talk about today?"
    st.session_state.initial_audio = synthesize_speech(initial_response)
    if st.session_state.initial_audio:
        st.audio(st.session_state.initial_audio, format='audio/mp3')
    else:
        st.error("Failed to synthesize initial speech.")

# Capture user audio automatically and process it once recorded
audio_data = st_audiorec()

if audio_data is not None:
    # Transcribe the audio input to text
    transcription = transcribe_audio(audio_data)

    # Send the transcription to the Gemini model
    response = st.session_state.chat.send_message(transcription + "\n [" + initial_prompt + "]" , stream=True)

    # Generate a response and convert it to speech
    generated_text = ''.join([chunk.text for chunk in response])
    audio_content = synthesize_speech(generated_text)

    # Automatically play back the generated response
    if audio_content:
        st.audio(audio_content, format='audio/mp3')
    else:
        st.error("Failed to synthesize speech.")
