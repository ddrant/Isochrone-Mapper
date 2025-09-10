# state.py

import streamlit
import folium

class IsochroneState:
    def __init__(self, geojson, metadata):
        self.geojson = geojson
        self.metadata = metadata
        # any other analysis-specific stuff


class MapState:
    def __init__(self):
        self.isochrones = {}  # id: IsochroneState
        self.markers = []
        self.focus_id = None  # which isochrone to zoom to
        # add more as needed

    def add_isochrone(self, id, geojson, metadata):
        self.isochrones[id] = IsochroneState(geojson, metadata)

    def remove_isochrone(self, id):
        self.isochrones.pop(id, None)

    def clear(self):
        self.isochrones.clear()
        self.markers.clear()
        self.focus_id = None