from groq import Groq
import requests
import json
from datetime import datetime
import streamlit as st
import sys
import os

try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    # Fallback to environment variable if secrets not configured
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ_API_KEY not found. Please set it in secrets or environment variables.")
        st.stop()

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Say hello and tell me a joke!"}
    ]
)

print(response.choices[0].message.content)