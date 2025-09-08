# utils.py
import os
import streamlit as st
from dotenv import load_dotenv


# retrieve the Open Route Service api key
def get_api_key(name="ORS_API_KEY") -> str:
    # Try Streamlit secrets first
    key = st.secrets.get(name) if hasattr(st, "secrets") else None
    if key:
        return key

    # Fallback: .env
    load_dotenv()
    key = os.getenv(name)
    if key:
        return key

    raise ValueError(f"{name} not found in environment or st.secrets")