import requests
import streamlit as st
from constants import COUNTRY_TO_ALPHA2





##########################################################################################
# Function could need reviewing / polishing
#########################################################################################
@st.cache_data
def find_address_cords(
        api_key:str,
        address:str, 
        country="United Kingdom of Great Britain and Northern Ireland",
        focus_point=[-0.12574000, 51.50853000]          # maybe later on can change focus_point to their last search? (also depends on country)
        ):
    """
    focus_point : the location to focus the address search near
         [lon: float, lat: float] : default [-0.12574000, 51.50853000] (London)
    """

    if address.strip() == "":
        return None # empty string entered - do not attempt to search.


    # Openrouteservice's geocode search api rul
    url = f"https://api.openrouteservice.org/geocode/search"

    params = {
        "api_key": api_key,
        "text":address,
        "size": 1, # number of results to return from search
        #"focus.point.lon": focus_point[0],
        #"focus.point.lat": focus_point[1],
        "boundary.country": COUNTRY_TO_ALPHA2[country]            #< -- to FORCE GB only results
    }

    # handle bad requests or no address match
    try: 
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        #if response.status_code != 200:
        #    print(f"Error {response.status_code}: {response.text}")
        #    return None
        data = response.json()
        
        features = data.get("features", [])
        if not features:
            st.sidebar.warning("No results found. Try another spelling or add a post code")
            return None # No match found

        coords = features[0]["geometry"]["coordinates"] # [lon, lat] format
        return coords
    
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except (KeyError, IndexError, TypeError):
        return None