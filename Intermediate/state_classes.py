# state.py

import streamlit as st
import folium
from dataclasses import dataclass, field
from typing import OrderedDict, Optional, Tuple
from constants import FOLIUM_MARKER_COLORS
from folium.plugins import MiniMap, MousePosition, BeautifyIcon

# move to contants?
ISOCHRONE_COLORS = [
    "#2A81CB", "#ff7f0e", "#2bd32b", "#d62728", "#9338e7",
    "#f54177", "#e377c2", "#37f3e3", "#bcbd22", "#046e1b"
]

@dataclass
class IsochroneLayerState:
    geojson: dict = field(default_factory=dict) # or can just check and compare if these are the same?
    # center: Optional[Tuple[float, float]] = None # need to check this before adding new isochrone laters
    marker_color: str = 'blue'
    isochrone_color: str = None
    map_zoom: int = 10
    transport_mode: str = 'car' # this 
    time_allowance_mins: int = None # this 

    def __post_init__(self):
        if self.map_zoom is None:
            self.map_zoom = 10

        # set the isochrone color to match the marker color if not specified
        if self.isochrone_color and not is_hex_color(self.isochrone_color):
            self.isochrone_color = FOLIUM_MARKER_COLORS[self.isochrone_color]
        elif is_hex_color(self.marker_color):
            self.isochrone_color = self.marker_color           
        else: 
            self.isochrone_color = FOLIUM_MARKER_COLORS[self.marker_color]


    @property
    def center(self) -> Tuple[float, float]:
        """Returns (lat, lon) center from geoJSON"""
        return tuple(self.geojson['features'][0]['properties']['center'][::-1])
    
    @property
    def lat(self) -> float:
        return self.center[0]
    
    @property
    def lon(self) -> float:
        return self.center[1]
        



@dataclass
class MapState:
    origin: Optional[Tuple[float, float]] = (51.5, 0)  # (lat, lon)
    isochrones: OrderedDict[int, IsochroneLayerState] = field(default_factory=OrderedDict)
    next_id: int = 1 # starts with 1, next id to give the added isochrone
    focus_id: int = None 
    selected_location: Optional[Tuple[float, float]] = None # (lat, lon) for the search adress or clicked location
    use_map: bool = False # if true, use the map clicked location instead of searched address


    def add_isochrone(self, geojson, marker_color=None, 
                      isochrone_color=None, map_zoom=None, transport_mode='car', time_allowance_mins = 30):
        
        # Choose color based on current count
        if marker_color == None:
            index = len(self.isochrones) % len(ISOCHRONE_COLORS)
            marker_color = ISOCHRONE_COLORS[index]

        # need to add some default randomness for the marker and isochrone colors when there are multiple isochrones and not specified
        new_layer = IsochroneLayerState(
            geojson=geojson, 
            marker_color=marker_color, 
            isochrone_color=isochrone_color, 
            map_zoom=map_zoom, 
            transport_mode=transport_mode,
            time_allowance_mins=time_allowance_mins
            )
        
        # to check for duplicates (exact same params)
        for layer in self.isochrones.values():
            if (
                layer.center == new_layer.center and
                layer.transport_mode == new_layer.transport_mode and
                layer.time_allowance_mins == time_allowance_mins
            ):
                print("Isochrone at this location already exists, not adding.")
                st.session_state.duplicate_isochrone_warning = True
                return
        
        # if layer doesnt already exist, add it to the dict
        self.isochrones[self.next_id] = new_layer
        
        self.focus_id = self.next_id
        self.next_id += 1

        self.selected_location = None # clear the selected location after adding the isochrone


    def remove_isochrone(self, id=None):
        if self.isochrones == {}:
            return
        
        if id is None:
            # remove the last added isochrone
            id = max(self.isochrones.keys())

        self.isochrones.pop(id, None)
        # re order the ids 
        self.isochrones = OrderedDict((new_id, layer) for new_id, layer in enumerate(self.isochrones.values(), start=1))
        self.next_id = len(self.isochrones) + 1
        self.focus_id = max(self.isochrones.keys()) if self.isochrones else None


    def clear(self):
        self.isochrones.clear()
        self.markers.clear()
        self.focus_id = None

    def select_isochrone(self, id: int):
        self.selected_location = self.isochrones[id].center
        self.focus_id = id

    def add_selected_location_marker(self, map: folium.Map):
        if self.selected_location:
            print("ENTERED selected location marker addition")
            folium.Marker(
                location=self.selected_location,
                tooltip="Selected location",
                icon=folium.Icon(prefix='fa-regular fa', icon="flag", color="red")#,
                #size='large'
            ).add_to(map)


    def _create_base_map(self, location: tuple[float, float], zoom: int = 6, min_zoom:int = 2) -> folium.Map:
        """
        Internal helper to create a Folium map with consistent defaults
        (center, zoom, min_zoom, and FA icons).
        """

        m = folium.Map(location=location, zoom_start=zoom, min_zoom=min_zoom)

        # Inject Font Awesome 5 (includes car, bicycle, walking, etc.)
        fa5_href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
        m.get_root().html.add_child(
            folium.Element(f'<link rel="stylesheet" href="{fa5_href}">')
        )

        return m
    

    # render and return the folium map
    def build_map(self) -> folium.Map:

        # if last action was a search address or map click, center on that location
        if self.selected_location:
            
            print(f"selected location: {self.selected_location}")
            map = self._create_base_map(location=self.selected_location, zoom=10, min_zoom=2)

        # else if there are isochrones, center on the focused one
        elif self.focus_id and self.focus_id in self.isochrones:
            
            print(f"focus id: {self.focus_id}")
            print(f"center : {self.isochrones[self.focus_id].center}")
            map = self._create_base_map(location=self.isochrones[self.focus_id].center, 
                                        zoom=self.isochrones[self.focus_id].map_zoom,  # map this depend on the area of the isochrone later on?
                                        min_zoom=2)
        
        else:
        
            map = self._create_base_map(location=self.origin, zoom=6, min_zoom=2)

#        folium.TileLayer("CartoDB dark_matter").add_to(map)
 #       folium.TileLayer("CartoDB positron").add_to(map)
        MousePosition().add_to(map)
        MiniMap(toggle_display=True).add_to(map)
        # add each isochrone layer to the map
        for id, isochrone in self.isochrones.items():
            add_isochrone_layer(map=map, layer=isochrone)


        # add the selected location marker last so its on top
        self.add_selected_location_marker(map)

        return map







########

# SEPERATE FUNCTION FOR NOW

###########



def add_isochrone_layer(map: folium.Map, layer: IsochroneLayerState) -> None:
    """
    transport_mode: str {'car', 'bicycle', 'person-walking', 'public-transport'}
    """
    TRANSPORT_MODE_MAP = {
        'driving-car': 'car',  
        'cycling-regular': 'bicycle',
        'foot-walking': 'person-walking',
    }
    print(f"transport mode map keys: {TRANSPORT_MODE_MAP.keys()}")
    transport_icon = TRANSPORT_MODE_MAP.get(layer.transport_mode, 'car') # default to 'car' if not found
    # icon_transport_map = {'car': 'car', 'bicycle': 'bicycle', 'foot':'person-walking'}
    # NEED TO MAP THE LAYER TRANSPORT MODE TO THE FONT AWESOME ICON NAME

    # CHANGE THIS NAME
    # now to add the isochrone polygon to the map 
    folium.GeoJson(layer.geojson, name="Isochrone 30mins driving", color=layer.isochrone_color).add_to(map)
    
    # Design the icon for the marker
    icon=BeautifyIcon(
        icon=transport_icon,   # FA6 classes work if you load FA6 CSS
        icon_shape='marker',
        background_color=layer.marker_color,
        text_color='white',
        border_color='black',
        border_width=1,
        inner_icon_style="margin-top:1px; margin-right:3px; font-size:16px;"
    )

    # Create the marker for the starting point
    folium.Marker(
        location=[layer.lat, layer.lon], 
        tooltip='Starting location', # change to add id? and or name?
        icon=icon
        #icon=folium.Icon(prefix='fa', icon=transport_icon, color=layer.marker_color)
    ).add_to(map)





    print(f"marker color: {layer.marker_color}")
    return None




# possibly move to utils.py or something

import re # regex 
HEX_COLOR_PATTERN = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')

def is_hex_color(s: str) -> bool:
    return bool(HEX_COLOR_PATTERN.match(s))