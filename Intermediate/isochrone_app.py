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


print("START OF APP")
print("===================================")

###################################################################################################

# START OF APP/UI CODE

###################################################################################################


st.title("Generate youre Isochrone")
#st.header("How far can you travel?")


if "ORS_API_KEY" not in st.session_state:
    st.session_state.ORS_API_KEY = get_api_key()


if "map_session_state" not in st.session_state:
    st.session_state.map_session_state = MapState()




# a warning to show if no starting location has been set before generating an isochrone
if "location_warning" not in st.session_state:
    st.session_state.location_warning = False


if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "selected_history" not in st.session_state:
    st.session_state.selected_history = None 


# maybe change this to reset search later on
if "reset_address" not in st.session_state:
    st.session_state.reset_address = True

if "search_warning" not in st.session_state:
    st.session_state.search_warning = False

if "duplicate_isochrone_warning" not in st.session_state:
    st.session_state.duplicate_isochrone_warning = False

print(f"show warning: {st.session_state.search_warning} ")


if "reset_last_clicked" not in st.session_state:
    st.session_state.reset_last_clicked = False





def on_address_search_change():
    if st.session_state.address_str != "":
        st.session_state.selected_history = None # clear the previous search selection if a new address is typed in
        #st.session_state.reset_address = False # to prevent resetting the address input box when typing in it
        print("address search change")
        print(f"selected history after change: {st.session_state.selected_history}")


def on_previous_search_change():
    if st.session_state.selected_history is not None:
        st.session_state.address_str = "" # clear the address input box if a previous search is selected
        
        st.session_state.map_session_state.selected_location = st.session_state.selected_history["coords"]
        print(st.session_state.selected_history["address"])
        print(st.session_state.selected_history["coords"])
        print("previous search change")
        print(f"address str after change: {st.session_state.address_str}")









#####################################

# Sidebar

#####################################]

if st.session_state.map_session_state.selected_location is not None:
    st.session_state.location_warning = False # clear location warning if it was on

# To handle the toggle between address search and map click to set starting location

# set the previous search mode to watch for changes
prev_use_map = st.session_state.map_session_state.use_map

# toggle for search mode (address search or map click)
st.session_state.map_session_state.use_map = st.sidebar.toggle(
    "Click to set location", 
    value=False, 
    help="Toggle between searching for an address or clicking on the map to set a location"
    )

# if the toggle has changed, clear the selected location 
if st.session_state.map_session_state.use_map != prev_use_map:
    st.session_state.map_session_state.selected_location = None
    st.session_state.selected_history = ""
    st.session_state.reset_address = True # reset the address input box when switching to map click mode
    st.session_state.search_warning = False # clear any warnings when switching modes
    st.session_state.duplicate_isochrone_warning = False # clear duplicate warning when switching modes
    st.session_state.location_warning = False # clear location warning when switching modes
    print("clearing selected location")
    print(f"selected location after clearing: {st.session_state.map_session_state.selected_location}")
    st.session_state.reset_last_clicked = True # to reset the last clicked location on the map when switching to map click mode



# warnings and resets 


# CAN MOVE THIS INTO A WITH ST.SIDEBAR BLOCK LATER

# Creating the address str in session state so we can reset it after search
#if "address_str" not in st.session_state:
if st.session_state.reset_address:
    st.session_state.address_str = ""
    st.session_state.reset_address = False

# no search results warning
if st.session_state.search_warning:
    st.sidebar.warning("No results found. Try another spelling or add a postcode")

print(f"duplicate warning: {st.session_state.duplicate_isochrone_warning} ")

# duplicate isochrone warning
if st.session_state.duplicate_isochrone_warning:
    st.sidebar.warning("Isochrone at this location with these parameters already exists.")

print(f"duplicate warning after: {st.session_state.duplicate_isochrone_warning}")


print(f"location warning: {st.session_state.location_warning} ")
if st.session_state.location_warning:
    st.sidebar.warning("No location set. Please search for an address or click on the map to set a location.")
print(f"location warning after: {st.session_state.location_warning} ")





# functionality 

with st.sidebar:
    #with st.form("search_form"):

        

        
    
        # Address search box
        st.text_input('Search', placeholder="address", key="address_str", 
                      disabled=st.session_state.map_session_state.use_map,
                      on_change=on_address_search_change)


        # country selectbox for address search
        country_search = st.selectbox(
            "Select the country",
            options = sorted(COUNTRY_TO_ALPHA2.keys()),
            index=233,
            disabled=st.session_state.map_session_state.use_map
        )

        #find_address = st.form_submit_button("Find Address", disabled=st.session_state.map_session_state.use_map, use_container_width=True)
        
        find_address = st.button("Find Address", disabled=st.session_state.map_session_state.use_map, use_container_width=True)
        # previous searches selectbox or suggestions
        st.selectbox(
            "or previous searches", 
            options= [None] + st.session_state.search_history,
            index=0, 
            key="selected_history",
            format_func=lambda x: f"{x['address']}, {x['country']}" if x and x['address'] else "",
            disabled=st.session_state.map_session_state.use_map,
            on_change=on_previous_search_change
            )

        st.markdown("---")


    #with st.form("isochrone params"):
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
        #submitted = st.form_submit_button("Generate Isochrone", use_container_width=True)
        submitted = st.button("Generate Isochrone", use_container_width=True)

   #submitted = st.button("Find address and Generate Isochrone", use_container_width=True, disabled=use_map_toggle)
    
        remove_last = st.sidebar.button("Remove last isochrone", use_container_width=True)




##########################################

# main?

##########################################
help = st.popover('Test')

with help:
    col1, col2 = st.columns(2)
    with col1:
        rerun_btn = st.button("click")
    with col2:
        st.write(f"Selected location:" + str(st.session_state.map_session_state.selected_location) if st.session_state.map_session_state.selected_location else "None")

if rerun_btn:
    st.rerun()


# might not be doing anything anymore
if "map_state_tmp" in st.session_state:
    help.write(f"current coords: {st.session_state.map_state_tmp}")











if find_address:
    print(f"session state address str: {st.session_state.address_str}")
    #if 
    lon_lat_coords = find_address_cords(api_key = st.session_state.ORS_API_KEY, address=st.session_state.address_str, country=country_search)

    if lon_lat_coords is not None:
        lat_lon_coords = (lon_lat_coords[1], lon_lat_coords[0]) # in (lat, lon) format for folium
        st.session_state.map_session_state.selected_location = lat_lon_coords # in (lat, lon) format for folium


        # st.session_state.search_history.append(st.session_state.address_str.strip())
        st.session_state.search_history.append(
            {"address": st.session_state.address_str.strip(), 
             "country": country_search, 
             "coords": lat_lon_coords}
            )

        # not currently used
        st.session_state.last_searched = st.session_state.address_str.strip() # maybe we want to store search address for isochrone

        # reset warnings
        st.session_state.search_warning = False
    else:
        print("turning search warning on")
        st.session_state.search_warning = True

    st.rerun() # for the warnings






if submitted:
    # can remove later
    st.text("submitted")
    
    # generate
    # reset the duplicate warning flag when new search is made
    st.session_state.duplicate_isochrone_warning = False

    # If the address coords are found successfully
    if st.session_state.map_session_state.selected_location is not None:


        lat, lon = st.session_state.map_session_state.selected_location
        geoJSON = get_isochrone(api_key=st.session_state.ORS_API_KEY, lon=lon, lat=lat,
                                profile=transport_mode, minutes=time_allowance)


        # Add the isochrone to the map state
        st.session_state.map_session_state.add_isochrone(geojson=geoJSON, transport_mode=transport_mode, time_allowance_mins=time_allowance)

        # now we can remove the warning flag if it was on
        st.session_state.show_warning = False
    else:
        print("no location set")
        st.session_state.location_warning = True
        # change to no location set warning
        #st.session_state.show_warning = True
    
    
    # reset the coords session state variable
    #st.session_state.coords = None
    print(f"selected location: {st.session_state.map_session_state.selected_location}")
    
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







######
# COL 1 - MAP
######

with col1: 
    # call to render Folium map in Streamlit
    st_data = st_folium(map, height=700, use_container_width=True)




if st.session_state.reset_last_clicked:
    st_data['last_clicked'] = None
    st.session_state.reset_last_clicked = False

if st.session_state.map_session_state.use_map and st_data['last_clicked']:

    st.session_state.map_session_state.selected_location = (st_data['last_clicked']['lat'], st_data['last_clicked']['lng']) # (lat, lon) tuple for folium
    st.rerun()



st_data


