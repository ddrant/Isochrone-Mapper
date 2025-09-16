# state.py

import streamlit as st
import folium
from dataclasses import dataclass, field
from typing import OrderedDict, Optional, Tuple


@dataclass
class IsochroneLayerState:
    geojson: dict = field(default_factory=dict) # or can just check and compare if these are the same?
    center: Optional[Tuple[float, float]] = None # need to check this before adding new isochrone laters
    marker_color = 'blue'
    isochrone_color=None
    map_zoom = 13
    transport_mode = 'car' # this 
    # time_minutes: int = None # this 

    def __post_init__(self):
        if self.center == None:
            self.center = tuple(self.geojson['features'][0]['properties']['center'][::-1])
            st.write("center: ", self.center)

        # any other analysis-specific stuff

@dataclass
class MapState:
    origin: Optional[Tuple[float, float]] = (51.5, 0)  # (lat, lon)
    isochrones: OrderedDict[int, IsochroneLayerState] = field(default_factory=OrderedDict)
    next_id: int = 1 # starts with 1, next id to give the added isochrone
    focus_id: int = None 



    def add_isochrone(self, geojson, center=None, 
                   marker_color='blue', isochrone_color=None, map_zoom=13, transport_mode='car'):
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
            



        return map
