# App to find and display ischrones with given parameters using ORS api and streamlit, folium, etc
# creation date: 07/09/2025 (d/m/y)
# last updated: 16/09/2025

# custom function files
from utils import *
from constants import *
from services import *
from state_classes import *
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

# Creating the address str in session state so we can reset it after search

with st.sidebar.form("search_form"):
    # Address search box
    address_input = st.sidebar.text_input('Search', placeholder="address")#, key="address_str")

    # country selectbox for address search
    country_search = st.sidebar.selectbox(
        "Select the country of the address",
        options = sorted(COUNTRY_TO_ALPHA2.keys()),
        index=233
    )

    # remove later
    st.sidebar.text(country_search)

    # generate isochrone (search) button 
    submitted = st.sidebar.button("Generate Isochrone")






##########################################

# main?

##########################################
help = st.popover('Test')



help.button("click")
if "map_state_tmp" in st.session_state:
    help.write(f"current coords: {st.session_state.map_state_tmp}")

if "map_session_state" not in st.session_state:
    st.session_state.map_session_state = MapState()



coords = find_address_cords(api_key = st.session_state.ORS_API_KEY, address=address_input.strip(), country=country_search)
if coords:
    st.session_state.coords = coords



# No result warning in the main window
if "coords" in st.session_state and coords is None: 
    st.sidebar.warning("No results found. Try another spelling or add a postcode")

# just for loading the last clicked location as center spot at the moment, need to move to map state later
if "coords" not in st.session_state and "last_clicked" in st.session_state:
    
    map = folium.Map(location = st.session_state.last_clicked, zoom_start=13, min_zoom=2)
    
    #if "last_clicked" not in st.session_state:
    #    st.session_state.map_session_state = MapState()
    #    map = st.session_state.map_session_state.build_map()
    #    #map = folium.Map(location = [START_LAT,START_LON], zoom_start=6, min_zoom=2)
    #else: 
else:
   
    #map = folium.Map(location=coords_folium)
    if submitted:
        st.text("submitted")
        # search for the coords of the address
        coords = find_address_cords(api_key = st.session_state.ORS_API_KEY, address=address_input.strip(), country=country_search)
        if coords:
            st.session_state.coords = coords


        if coords != None: # remove later temp
            coords_folium = st.session_state.coords[::-1] # in [lat, lon] format
            geoJSON = get_isochrone(api_key=st.session_state.ORS_API_KEY, lon=coords[0], lat=coords[1])

        # call the function to generate isochrone and add to the map
        #plot_isochrone(map=map, geoJSON=geoJSON)
            st.session_state.map_session_state.add_isochrone(geojson=geoJSON)
    
    
    map = st.session_state.map_session_state.build_map()






if "map_state_tmp" in st.session_state and st.session_state.map_state_tmp is not None:
    
    st.session_state.last_clicked = [st.session_state.map_state_tmp['lat'], st.session_state.map_state_tmp['lng']]
    folium.Marker(
        location=list(st.session_state.last_clicked),
        tooltip='Starting location', 
        icon=folium.Icon(prefix='fa', icon='car', color='blue')
        ).add_to(map) # marker needs to be in [lat, lon] format



# call to render Folium map in Streamlit
st_data = st_folium(map, height=600, use_container_width=True)




st.write("Last Clicked:")
st_data['last_clicked']

if st_data['last_clicked']:
    st.session_state.map_state_tmp = st_data['last_clicked']



st_data

st.sidebar.button("button2")


