import folium
from folium import plugins
from streamlit_folium import st_folium
import streamlit as st
import re

# --- 1. UNIVERSAL COORDINATE CONVERSION ENGINE ---
def parse_coordinate(coord_str):
    """Safely converts DMS or Decimal Minutes strings to Decimal Degrees."""
    # Replace commas with dots for decimal handling, make uppercase
    clean_str = coord_str.replace(',', '.').upper()
    
    # Extract all numbers and the directional letter
    numbers = re.findall(r"[\d\.]+", clean_str)
    direction_match = re.search(r"[NSWE]", clean_str)
    
    if not numbers or not direction_match:
        return 0.0
        
    direction = direction_match.group()
    
    # Assign values based on how many numbers were found
    degrees = float(numbers[0]) if len(numbers) > 0 else 0.0
    minutes = float(numbers[1]) if len(numbers) > 1 else 0.0
    seconds = float(numbers[2]) if len(numbers) > 2 else 0.0
    
    # Calculate final decimal
    decimal = degrees + (minutes / 60) + (seconds / 3600)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def parse_table(coord_list):
    return [[parse_coordinate(lat), parse_coordinate(lon)] for lat, lon in coord_list]

# --- 2. EXACT DIGITAL TWIN DATA ---
# Pilot Station
pilot_station = [parse_coordinate("35° 18',60 N"), parse_coordinate("003° 09',70 W")]
shoal = [parse_coordinate("35° 19' 14\" N"), parse_coordinate("3° 06' 39\" W")]

# Access Channel (C1 -> C3 -> C5 -> C7 -> C8 -> C6 -> C4 -> C2)
access_channel_raw = [
    ["35° 17' 18\" N", "003° 09' 13\" W"], # C1
    ["35° 16' 56\" N", "003° 09' 15\" W"], # C3
    ["35° 16' 35\" N", "003° 09' 23\" W"], # C5
    ["35° 16' 13\" N", "003° 09' 42\" W"], # C7 (Landward)
    ["35° 16' 01\" N", "003° 09' 29\" W"], # C8 (Landward)
    ["35° 16' 29\" N", "003° 09' 08\" W"], # C6
    ["35° 16' 49\" N", "003° 08' 59\" W"], # C4
    ["35° 17' 10\" N", "003° 08' 50\" W"]  # C2
]

# West Anchorage
west_anchorage_raw = [
    ["35° 14' 56\" N", "003° 15' 49\" W"], # MW1
    ["35° 14' 56\" N", "003° 12' 08\" W"], # MW2
    ["35° 16' 38\" N", "003° 12' 08\" W"], # MW3
    ["35° 16' 38\" N", "003° 15' 49\" W"]  # MW4
]

# Process Arrays
access_channel = parse_table(access_channel_raw)
west_anchorage = parse_table(west_anchorage_raw)

# Derived Inner Port Zones (Estimated from C7/C8 landward bounds)
turning_basin = [
    access_channel[3], access_channel[4], 
    [35.2630, -3.1530], [35.2650, -3.1600] # Estimations for the basin arc
]

# --- 3. INITIALIZE THE MAP & ECDIS PLUGINS ---
port_map = folium.Map(location=[35.2800, -3.1500], zoom_start=12, tiles='CartoDB positron')

# Essential Planning Tools
port_map.add_child(plugins.MeasureControl(position='topleft', primary_length_unit='nauticalmiles'))
formatter = "function(num) {return L.Util.formatNum(num, 5) + ' º ';};"
plugins.MousePosition(
    position='topright', separator=' | ', empty_string='NaN', lng_first=False,
    num_digits=5, prefix='Cursor:', lat_formatter=formatter, lng_formatter=formatter,
).add_to(port_map)
plugins.Draw(export=True, position='topleft').add_to(port_map)

# --- 4. DRAW THE MARITIME LAYERS ---
# Anchorage
folium.Polygon(
    locations=west_anchorage, color='magenta', weight=2, fill=True, fill_opacity=0.15, 
    popup='<b>West Anchorage Zone</b><br>Limits: MW1 - MW4'
).add_to(port_map)

# Access Channel & Basin
folium.Polygon(
    locations=access_channel, color='black', weight=2, fill=True, fill_color='lightblue', fill_opacity=0.4, 
    popup='<b>Access Channel</b><br>Depth: -22.0m<br>Width: 440m<br>Length: 2,257m'
).add_to(port_map)

folium.Polygon(
    locations=turning_basin, color='navy', weight=1, fill=True, fill_opacity=0.2, dash_array='4',
    popup='<b>Turning Basin (Cercle d\'évitage)</b><br>Depth: -22.0m'
).add_to(port_map)

# Critical Marks
folium.Marker(
    location=pilot_station, 
    popup="<b>Pilot Boarding Point</b><br>Approx 3NM North of entrance", 
    icon=folium.Icon(color="red", icon="flag")
).add_to(port_map)

folium.CircleMarker(
    location=shoal, radius=6, color="orange", fill=True, fill_color="orange",
    popup="<b>Isolated Shoal</b><br>Depth: 15m"
).add_to(port_map)

# --- 5. RENDER IN STREAMLIT ---
st.set_page_config(layout="wide")
st.title("⚓ Nador West Med - Passage Plan Drafting")
st.markdown("Use the drawing toolbar to plot tracks, set waypoints, and export standard GeoJSON routes. Measure distances in Nautical Miles.")

# Render map spanning app width
st_folium(port_map, width=1200, height=750)
