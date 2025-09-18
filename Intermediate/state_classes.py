# state.py

import streamlit as st
import folium
from dataclasses import dataclass, field
from typing import OrderedDict, Optional, Tuple
from constants import FOLIUM_MARKER_COLORS


@dataclass
class IsochroneLayerState:
    geojson: dict = field(default_factory=dict) # or can just check and compare if these are the same?
    # center: Optional[Tuple[float, float]] = None # need to check this before adding new isochrone laters
    marker_color: str = 'blue'
    isochrone_color: str = None
    map_zoom: int = 13
    transport_mode = 'car' # this 
    # time_minutes: int = None # this 

    def __post_init__(self):

        # set the isochrone color to match the marker color if not specified
        if self.isochrone_color:
            self.isochrone_color = FOLIUM_MARKER_COLORS[self.isochrone_color]
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


    def add_isochrone(self, geojson, marker_color='blue', 
                      isochrone_color=None, map_zoom=13, transport_mode='car'):
        
        # need to add some default randomness for the marker and isochrone colors when there are multiple isochrones and not specified
        self.isochrones[self.next_id] = IsochroneLayerState(geojson=geojson)
        self.focus_id = self.next_id
        self.next_id += 1


    def remove_isochrone(self, id):
        self.isochrones.pop(id, None)
        # re order the ids 


    def clear(self):
        self.isochrones.clear()
        self.markers.clear()
        self.focus_id = None


    # render and return the folium map
    def build_map(self) -> folium.Map:

        if self.isochrones == {}:
            map = folium.Map(location = self.origin, zoom_start=6, min_zoom=2)

        else:
            # load all the isochrones in the dict to the map, set the focus of the map based on the last added isochrone 
            # or last clicked location if thats more recent
            print(f"focus id: {self.focus_id}")
            print(f"center : {self.isochrones[self.focus_id].center}")
            map = folium.Map(location=self.isochrones[self.focus_id].center, zoom_start=13, min_zoom=2)
            

        for id, isochrone in self.isochrones.items():
            # call the plot for each isochrone
            add_isochrone_layer(map=map, layer=isochrone)


        return map







########

# SEPERATE FUNCTION FOR NOW

###########



def add_isochrone_layer(map: folium.Map, layer: IsochroneLayerState) -> None:
    """
    transport_mode: str {'car', 'bicycle', 'person-walking', 'public-transport'}
    """

    # icon_transport_map = {'car': 'car', 'bicycle': 'bicycle', 'foot':'person-walking'}
    

    # CHANGE THIS NAME
    # now to add the isochrone polygon to the map 
    folium.GeoJson(layer.geojson, name="Isochrone 30mins driving", color=layer.isochrone_color).add_to(map)
    
    # Inject FA 6 (Font Awesone 6) CSS for specific icons   
    fa6_href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"
    fa6_link_tag = f'<link rel="stylesheet" href="{fa6_href}">'
    root_html = map.get_root().html
    # Check if FA6 link already added
    if fa6_href not in str(root_html.render()):  # basic check to avoid duplicate injection
        root_html.add_child(folium.Element(fa6_link_tag))
    

    # Create the marker for the starting point
    folium.Marker(
        location=[layer.lat, layer.lon], 
        tooltip='Starting location', # change to add id? and or name?
        icon=folium.Icon(prefix='fa', icon=layer.transport_mode, color=layer.marker_color)
    ).add_to(map)

    return None
