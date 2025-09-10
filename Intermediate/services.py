import requests
import streamlit as st
from constants import COUNTRY_TO_ALPHA2, FOLIUM_MARKER_COLORS
import folium




##########################################################################################
# Function could need reviewing / polishing
#########################################################################################
@st.cache_data
def find_address_cords(
        api_key:str,
        address:str, 
        country="United Kingdom of Great Britain and Northern Ireland",
        focus_point=[-0.12574000, 51.50853000]          # maybe later on can change focus_point to their last search? (also depends on country) -  probably not worth it
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
        "boundary.country": COUNTRY_TO_ALPHA2[country]            # forces results to search only in this country
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
        # Sidebar warning for no results (can be removed? decide later)
        if not features:
            print("No match found when finding address coords")
            return None # No match found

        coords = features[0]["geometry"]["coordinates"] # [lon, lat] format
        return coords
    
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except (KeyError, IndexError, TypeError):
        return None
    





    ### 

    # Isochrone API caller

    ###



@st.cache_data
def get_isochrone(api_key: str, lon: float, lat: float, minutes: int = 30, profile: str = "driving-car") -> dict | None:

    url = f"https://api.openrouteservice.org/v2/isochrones/{profile}" # OpenRouteService Isochrone API url

    # auth and return types
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    # body/parameters for the isochrone api
    body = {
        "locations": [[lon, lat]],      # can include more than one location in one call?
        "range": [minutes * 60],        # convert the minutes input into seconds
        "units": "m",
        "attributes": ["area", "reachfactor"]   # add more in here for analysis stage. Population, etc
    }

    try: 
        response = requests.post(url=url, json=body, headers=headers)
        response.raise_for_status() # raises HTTPError 
        return response.json() # returns GeoJSON-style dict

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        st.error(f"Isochrone API request failed: {e}")  
        return None
    
    except (ValueError, KeyError, TypeError) as e:
        print(f"Response parsing failed {e}")
        return None



















####

# plotting function (temp)

#####

def plot_isochrone(map: folium.Map, geoJSON, lat=None, lon=None, 
                   marker_color='blue', isochrone_color=None, map_zoom=13, transport_mode='car') -> None:
    """
    transport_mode: str {'car', 'bicycle', 'person-walking', 'public-transport'}
    """

    # icon_transport_map = {'car': 'car', 'bicycle': 'bicycle', 'foot':'person-walking'}
    

    # to match the isochrone area colour with the marker colour we need to convert it into hex colour code when passing to folium.GeoJson()
    if isochrone_color is None:
        isochrone_color = FOLIUM_MARKER_COLORS[marker_color]
    else: 
        isochrone_color = FOLIUM_MARKER_COLORS[isochrone_color]

    isochrone_center = geoJSON['features'][0]['properties']['center']
    if lat is None:
        lat = isochrone_center[1]
    if lon is None:
        lon = isochrone_center[0]

    # now to add the isochrone polygon to the map 
    folium.GeoJson(geoJSON, name="Isochrone 30mins driving", color=isochrone_color).add_to(map)
    
    # Inject FA 6 CSS for specific icons
    fa6_link = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">'
    map.get_root().html.add_child(folium.Element(fa6_link))

    # Create the marker for the starting point
    folium.Marker(
        location=[lat, lon], 
        tooltip='Starting location', 
        icon=folium.Icon(prefix='fa', icon=transport_mode, color=marker_color)
    ).add_to(map)

    return None
