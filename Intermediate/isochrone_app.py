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
#st.header("How far can you travel?")


if "ORS_API_KEY" not in st.session_state:
    st.session_state.ORS_API_KEY = get_api_key()












if "show_warning" not in st.session_state:
    st.session_state.show_warning = False

if "duplicate_isochrone_warning" not in st.session_state:
    st.session_state.duplicate_isochrone_warning = False

print(f"show warning: {st.session_state.show_warning} ")
#####################################

# Sidebar

#####################################]


# pills options for search mode or select on map mode
use_map = st.sidebar.toggle("Click to set location", value=False, help="Toggle between searching for an address or clicking on the map to set a location")



# warnings and resets 

# maybe change this to reset search later on
if "reset_address" not in st.session_state:
    st.session_state.reset_address = True

# Creating the address str in session state so we can reset it after search
#if "address_str" not in st.session_state:
if st.session_state.reset_address:
    st.session_state.address_str = ""
    st.session_state.reset_address = False

# no search results warning
if st.session_state.show_warning:
    st.sidebar.warning("No results found. Try another spelling or add a postcode")

print(f"duplicate warning: {st.session_state.duplicate_isochrone_warning} ")

# duplicate isochrone warning
if st.session_state.duplicate_isochrone_warning:
    st.sidebar.warning("Isochrone at this location with these parameters already exists.")

print(f"duplicate warning after: {st.session_state.duplicate_isochrone_warning}")






# functionality 

with st.sidebar:
    with st.form("search_form"):
        # Address search box
        st.text_input('Search', placeholder="address", key="address_str", disabled=use_map)

        # country selectbox for address search
        country_search = st.selectbox(
            "Select the country of the address",
            options = sorted(COUNTRY_TO_ALPHA2.keys()),
            index=233,
            disabled=use_map
        )

        # add a find address button separate from the generate isochrone button
        # this will pin a marker on the map at the searched location
        # then they select the transport mode and time allowance, etc and hit generate isochrone
        # the marker can also be set by clicking on the map, which separates the need to press search address button
        find_address = st.form_submit_button("Find Address", disabled=use_map, use_container_width=True)


    
    with st.form("isochrone params"):
        # transport mode selectbox
        transport_mode = st.selectbox(
            "Select transport mode",
            options = ["driving-car", "cycling-regular", "foot-walking"],
            index=0
        )

        # time allowance slider
        time_allowance = st.slider(
            "Select time allowance (minutes)",
            min_value=5,
            max_value=60,
            value=30,
            step=5
        )

        # generate isochrone (search) button 
        submitted = st.form_submit_button("Generate Isochrone", use_container_width=True)

   #submitted = st.button("Find address and Generate Isochrone", use_container_width=True, disabled=use_map)
    
    remove_last = st.sidebar.button("Remove last isochrone", use_container_width=True)




##########################################

# main?

##########################################
help = st.popover('Test')
help.button("click")


if "map_state_tmp" in st.session_state:
    help.write(f"current coords: {st.session_state.map_state_tmp}")

if "map_session_state" not in st.session_state:
    st.session_state.map_session_state = MapState()







# just for loading the last clicked location as center spot at the moment, need to move to map state later
#if not st.session_state.coords and "last_clicked" in st.session_state:
#    
#    map = folium.Map(location = st.session_state.last_clicked, zoom_start=13, min_zoom=2)
#    
    #if "last_clicked" not in st.session_state:
    #    st.session_state.map_session_state = MapState()
    #    map = st.session_state.map_session_state.build_map()
    #    #map = folium.Map(location = [START_LAT,START_LON], zoom_start=6, min_zoom=2)
    #else: 

    

#map = folium.Map(location=coords_folium)
if submitted:
    # can remove later
    st.text("submitted")

    # reset the duplicate warning flag when new search is made
    st.session_state.duplicate_isochrone_warning = False

    # search for the coords of the address
    coords = find_address_cords(api_key = st.session_state.ORS_API_KEY, address=st.session_state.address_str, country=country_search)
    
    # If the address coords are found successfully
    if coords is not None:

        #coords_folium = coords[::-1] # in [lat, lon] format
        geoJSON = get_isochrone(api_key=st.session_state.ORS_API_KEY, lon=coords[0], lat=coords[1],
                                profile=transport_mode, minutes=time_allowance)


        # Add the isochrone to the map state
        st.session_state.map_session_state.add_isochrone(geojson=geoJSON, transport_mode=transport_mode, time_allowance_mins=time_allowance)

        # now we can remove the warning flag if it was on
        st.session_state.show_warning = False
    else:
        print("turning warning on")
        st.session_state.show_warning = True
    
    
    # reset the coords session state variable
    #st.session_state.coords = None
    print(f"coords: {coords}")
    
    # set the reset address flag to true to reset the address input box
    st.session_state.reset_address = True

    st.rerun() # rerun the app to reset the address input box and show warning if needed



if remove_last:
    st.session_state.map_session_state.remove_isochrone()
    #st.rerun()


map = st.session_state.map_session_state.build_map()



################# 

# Add columns for map and isochrones added info
col1, col2 = st.columns([4,1])






#################
# for last clicked
#################
if "map_state_tmp" in st.session_state and st.session_state.map_state_tmp is not None:
    
    st.session_state.last_clicked = [st.session_state.map_state_tmp['lat'], st.session_state.map_state_tmp['lng']]
    folium.Marker(
        location=list(st.session_state.last_clicked),
        tooltip='Starting location', 
        icon=folium.Icon(prefix='fa', icon='car', color='blue')
        ).add_to(map) # marker needs to be in [lat, lon] format


######
# COL 1 - MAP
######

with col1: 
    # call to render Folium map in Streamlit
    st_data = st_folium(map, height=700, use_container_width=True)




st.write("Last Clicked:")
st_data['last_clicked']

if st_data['last_clicked']:
    st.session_state.map_state_tmp = st_data['last_clicked']
    st.rerun()



st_data


