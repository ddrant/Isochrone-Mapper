# App to find and display ischrones with given parameters using ORS api and streamlit, folium, etc
# creation date: 07/09/2025 (d/m/y)
# last updated: 08/09/2025

# custom function files
from utils import *
from constants import *
from services import *

# packages
import streamlit as st
import pandas as pd 
import numpy as np
import folium
from streamlit_folium import st_folium # to use foliumn with streamlit


if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1

st.session_state.counter


########################################

# Page configuration

########################################



st.set_page_config(page_title="Isochrone Map", layout="wide", initial_sidebar_state="expanded")


################
# LOAD OpenRouteService API KEY
################



############################################

# CONSTANTS 

############################################

START_LAT = 51.5
START_LON = 0




###################################################################################################

# START OF APP/UI CODE

###################################################################################################


st.title("Generate youre Isochrone")
st.header("How far can you travel?")


if "ORS_API_KEY" not in st.session_state:
    st.session_state.ORS_API_KEY = get_api_key()










#####################################

# Sidebar

#####################################

# Address search box
address_str = st.sidebar.text_input('Search', placeholder="address")

# country selectbox for address search
country_search = st.sidebar.selectbox(
    "Select the country of the address",
    options = sorted(COUNTRY_TO_ALPHA2.keys()),
    index=233
)

st.sidebar.text(country_search)

# refresh button 
st.sidebar.button("Refresh")






##########################################

# main?

##########################################



coords = find_address_cords(api_key = st.session_state.ORS_API_KEY, address=address_str.strip(), country=country_search)
if coords:
    st.session_state.coords = coords



# No result warning in the main window
if "coords" in st.session_state and coords is None: 
    st.sidebar.warning("No results found. Try another spelling or add a postcode")


if "coords" not in st.session_state:
    map = folium.Map(location = [START_LAT,START_LON], zoom_start=6, min_zoom=2)
else:
    coords_folium = st.session_state.coords[::-1] # in [lat, lon] format

    map = folium.Map(location=coords_folium)

    geoJSON = get_isochrone(api_key=st.session_state.ORS_API_KEY, lon=coords[0], lat=coords[1])

    # call the function to generate isochrone and add to the map
    plot_isochrone(map=map, geoJSON=geoJSON)

    #folium.Marker(
    #    location=coords_folium,
    #    tooltip='Starting location', 
    #    icon=folium.Icon(prefix='fa', icon='car', color='blue')
    #    ).add_to(map) # marker needs to be in [lat, lon] format

# call to render Folium map in Streamlit
st_data = st_folium(map, height=600, use_container_width=True)


#coords_folium