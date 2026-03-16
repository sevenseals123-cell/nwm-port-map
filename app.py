import folium
from streamlit_folium import st_folium
import streamlit as st
import re

# --- 1. COORDINATE CONVERSION ENGINE ---
def dms_to_decimal(dms_str):
    """Converts a DMS string like '35°13'26"N' to Decimal Degrees."""
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

def parse_centers(coord_dict):
    """Takes a dict and returns parsed decimal coordinates."""
    return {name: [dms_to_decimal(lat), dms_to_decimal(lon)] for name, (lat, lon) in coord_dict.items()}

# --- 2. EXACT DATA FROM NWM TABLES ---

# Table 4: NWM Roadstead 
roadstead_raw = [
    ["35°13'26\"N", "003°13'17\"W"], # R1
    ["35°14'12\"N", "003°16'00\"W"], # R2
    ["35°21'37\"N", "003°16'00\"W"], # R3
    ["35°21'37\"N", "003°01'30\"W"]  # R4
]

# Table 5: West Anchorage Area
west_anchorage_area_raw = [
    ["35°14'56\"N", "003°15'49\"W"], # MW1
    ["35°14'56\"N", "003°12'08\"W"], # MW2
    ["35°16'38\"N", "003°12'08\"W"], # MW3
    ["35°16'38\"N", "003°15'49\"W"]  # MW4
]

# Table 6: West Anchorage Position Centres
west_anchorage_centers_raw = {
    "W1": ["35°15'23\"N", "003°15'24\"W"],
    "W2": ["35°15'23\"N", "003°14'27\"W"],
    "W3": ["35°15'23\"N", "003°13'31\"W"],
    "W4": ["35°15'23\"N", "003°12'34\"W"],
    "W5": ["35°16'11\"N", "003°14'57\"W"],
    "W6": ["35°16'11\"N", "003°13'58\"W"],
    "W7": ["35°16'11\"N", "003°12'59\"W"]
}

# Table 7: East Anchorage Area
east_anchorage_area_raw = [
    ["35°18'40\"N", "003°05'06\"W"], # ME1
    ["35°20'48\"N", "003°03'07\"W"], # ME2
    ["35°21'29\"N", "003°03'51\"W"], # ME3
    ["35°19'22\"N", "003°05'50\"W"]  # ME4
]

# Table 8: East Anchorage Position Centres
east_anchorage_centers_raw = {
    "E1": ["35°19'26\"N", "003°05'06\"W"],
    "E2": ["35°20'07\"N", "003°04'27\"W"],
    "E3": ["35°20'47\"N", "003°03'48\"W"]
}

# Table 9: Access Channel (Ordered down the Port side, up the Starboard side to form a perimeter)
access_channel_raw = [
    ["35°17'18\"N", "003°09'13\"W"], # C1
    ["35°16'56\"N", "003°09'15\"W"], # C3
    ["35°16'35\"N", "003°09'23\"W"], # C5
    ["35°16'13\"N", "003°09'42\"W"], # C7
    ["35°16'01\"N", "003°09'29\"W"], # C8
    ["35°16'29\"N", "003°09'08\"W"], # C6
    ["35°16'49\"N", "003°08'59\"W"], # C4
    ["35°17'10\"N", "003°08'50\"W"]  # C2
]

# --- 3. PROCESS THE COORDINATES ---
roadstead = parse_table(roadstead_raw)
west_anchorage = parse_table(west_anchorage_area_raw)
east_anchorage = parse_table(east_anchorage_area_raw)
access_channel = parse_table(access_channel_raw)

west_centers = parse_centers(west_anchorage_centers_raw)
east_centers = parse_centers(east_anchorage_centers_raw)

# Known Navigational Marks
pilot_station = [35.3100, -3.1616]
shoal = [35.3205, -3.1108]

# --- 4. INITIALIZE THE MAP ---
port_map = folium.Map(location=[35.2800, -3.1500], zoom_start=11, tiles='CartoDB positron')

# --- 5. DRAW THE LAYERS ---

# Outer Roadstead 
folium.Polygon(
    locations=roadstead, color='blue', weight=1, fill=True, fill_opacity=0.05, popup='NWM Roadstead'
).add_to(port_map)

# West Anchorage Area
folium.Polygon(
    locations=west_anchorage, color='magenta', weight=2, fill=True, fill_opacity=0.15, popup='West Anchorage Area'
).add_to(port_map)

# West Anchorage Centres
for name, coords in west_centers.items():
    folium.CircleMarker(
        location=coords, radius=3, color='magenta', fill=True, popup=f'West Anchor: {name}'
    ).add_to(port_map)

# East Anchorage Area
folium.Polygon(
    locations=east_anchorage, color='magenta', weight=2, fill=True, fill_opacity=0.15, popup='East Anchorage Area'
).add_to(port_map)

# East Anchorage Centres
for name, coords in east_centers.items():
    folium.CircleMarker(
        location=coords, radius=3, color='magenta', fill=True, popup=f'East Anchor: {name}'
    ).add_to(port_map)

# Access Channel (-22m)
folium.Polygon(
    locations=access_channel, color='black', weight=2, fill=True, fill_color='lightblue', fill_opacity=0.4, popup='Access Channel (-22m)'
).add_to(port_map)

# Nav Marks
folium.Marker(
    location=pilot_station, popup="Pilot Boarding Point", icon=folium.Icon(color="red", icon="info-sign")
).add_to(port_map)

folium.CircleMarker(
    location=shoal, radius=6, popup="Isolated Shoal (15m)", color="orange", fill=True, fill_color="orange"
).add_to(port_map)

# --- 6. RENDER IN STREAMLIT ---
st.title("Nador West Med - Port ECDIS Overview")
st.markdown("Interactive layout detailing roadsteads, anchorages, and the access channel.")
st_folium(port_map, width=900, height=600)
