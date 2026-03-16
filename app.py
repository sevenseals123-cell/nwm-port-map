import folium
from streamlit_folium import st_folium
import streamlit as st
import re

# 1. Coordinate Conversion Engine
def dms_to_decimal(dms_str):
    """Converts a DMS string like '35°13\'26"N' to Decimal Degrees."""
    # Matches numbers and the directional letter (N, S, E, W)
    parts = re.split(r'[^\d\w]+', dms_str.strip())
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    direction = parts[3].upper()
    
    decimal = degrees + (minutes / 60) + (seconds / 3600)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def parse_table(coord_list):
    """Takes a list of [Lat_str, Lon_str] and returns [[Lat_DD, Lon_DD], ...]"""
    return [[dms_to_decimal(lat), dms_to_decimal(lon)] for lat, lon in coord_list]

# 2. Input your Table Data Here
# NWM Roadstead (Table 4) - Already converted to DD in previous step, but using parser for consistency
roadstead_raw = [
    ["35°13'26\"N", "003°13'17\"W"], # R1
    ["35°14'12\"N", "003°16'00\"W"], # R2
    ["35°21'37\"N", "003°16'00\"W"], # R3
    ["35°21'37\"N", "003°01'30\"W"]  # R4
]

# --- PASTE DATA FROM YOUR IMAGES BELOW ---

# Table 5: West Anchorage (Example format, replace with your image text)
west_anchorage_raw = [
    ["35°15'00\"N", "003°15'00\"W"], # Replace with actual W1
    ["35°16'00\"N", "003°15'00\"W"], # Replace with actual W2
    ["35°16'00\"N", "003°14'00\"W"], # Replace with actual W3
    ["35°15'00\"N", "003°14'00\"W"]  # Replace with actual W4
]

# Table 6: East Anchorage
east_anchorage_raw = [
    # ["Lat", "Lon"],
]

# Table 8: Compulsory Pilotage Area
pilotage_area_raw = [
    # ["Lat", "Lon"],
]

# Table 9: Access Channel
access_channel_raw = [
    # ["Lat", "Lon"],
]

# 3. Process the Coordinates
roadstead = parse_table(roadstead_raw)
# west_anchorage = parse_table(west_anchorage_raw)
# east_anchorage = parse_table(east_anchorage_raw)
# pilotage_area = parse_table(pilotage_area_raw)
# access_channel = parse_table(access_channel_raw)

# Known Navigational Marks
pilot_station = [35.3100, -3.1616]
shoal = [35.3205, -3.1108]

# 4. Initialize the ECDIS-style Map
port_map = folium.Map(location=[35.3000, -3.1500], zoom_start=11, tiles='CartoDB positron')

# 5. Draw the Layers

# Outer Roadstead
folium.Polygon(
    locations=roadstead, color='blue', weight=1, fill=True, fill_opacity=0.05, popup='NWM Roadstead'
).add_to(port_map)

# Anchorages (Magenta is standard ECDIS for anchorage areas)
# folium.Polygon(locations=west_anchorage, color='magenta', weight=2, fill=True, fill_opacity=0.2, popup='West Anchorage').add_to(port_map)
# folium.Polygon(locations=east_anchorage, color='magenta', weight=2, fill=True, fill_opacity=0.2, popup='East Anchorage').add_to(port_map)

# Pilotage Area
# folium.Polygon(locations=pilotage_area, color='red', weight=2, dash_array='5, 5', fill=False, popup='Compulsory Pilotage').add_to(port_map)

# Access Channel (Grey/Blue shading)
# folium.Polygon(locations=access_channel, color='black', weight=1, fill=True, fill_color='lightblue', fill_opacity=0.4, popup='Access Channel (-22m)').add_to(port_map)

# Nav Marks
folium.Marker(location=pilot_station, popup="Pilot Boarding Point", icon=folium.Icon(color="red", icon="info-sign")).add_to(port_map)
folium.CircleMarker(location=shoal, radius=6, popup="Isolated Shoal (15m)", color="orange", fill=True, fill_color="orange").add_to(port_map)

# 6. Render in App
st.title("Nador West Med - ECDIS Passage Planning")
st_folium(port_map, width=900, height=600)
