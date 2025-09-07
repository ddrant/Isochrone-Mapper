# App to find and display ischrones with given parameters using ORS api and streamlit, folium, etc
# creation date: 07/09/2025 (d/m/y)
# last updated: 

import streamlit as st
import pandas as pd 
import numpy as np
import os 
from dotenv import load_dotenv

import folium


def get_api_key() -> str:
    # Try Streamlit secrets first
    key = st.secrets.get("ORS_API_KEY") if hasattr(st, "secrets") else None
    if key:
        return key

    # Fallback: .env
    load_dotenv()
    key = os.getenv("ORS_API_KEY")
    if key:
        return key

    raise ValueError("ORS_API_KEY not found in environment or st.secrets")


################
# LOAD OpenRouteService API KEY
################

# load the .env file 
if "ORS_API_KEY" not in st.session_state:
    load_dotenv()

    # Get the API key from the .env file
    st.session_state.ORS_API_KEY = os.getenv("ORS_API_KEY")


    if not st.session_state.ORS_API_KEY:
        raise ValueError("ORS_API_KEY not found in environment")









##########################################################################################
# Function could need reviewing 
#########################################################################################

import requests


@st.cache_data
def find_address_cords(address="16 Upper Hollingdean Road", focus_point=[-0.12574000, 51.50853000]):
    """
    focus_point : the location to focus the address search near
         [lon: float, lat: float] : default [-0.12574000, 51.50853000] (London)
    """
    # Openrouteservice's geocode search api rul
    url = f"https://api.openrouteservice.org/geocode/search"

    params = {
        "api_key": ORS_API_KEY,
        "text":address,
        "size": 1, # number of results to return from search
        "focus.point.lon": focus_point[0],
        "focus.point.lat": focus_point[1]
        # "boudary.country": "GB"           < -- to FORCE GB only results
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return None

    data = response.json()

    coords = data["features"][0]["geometry"]["coordinates"] # [lon, lat] format
    
    return coords




###################################################################################################

# START OF APP/UI CODE

###################################################################################################


st.title("Generate youre Isochrone")
st.header("How far can you travel?")

address_str = st.sidebar.text_input('Search', placeholder="address")


find_address_cords(address=address_str)


map = folium.map()

ORS_API_KEY = get_api_key()

