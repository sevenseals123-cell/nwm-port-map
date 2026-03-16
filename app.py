import folium
from folium import plugins
from streamlit_folium import st_folium
import streamlit as st
import re

# --- 1. UNIVERSAL COORDINATE CONVERSION ENGINE ---
def parse_coordinate(coord_str):
    """Safely converts DMS or Decimal Minutes strings to Decimal Degrees."""
    clean_str = coord_str.replace(',', '.').upper()
    numbers = re.findall(r"[\d\.]+", clean_str)
    direction_match = re.search(r"[NSWE]", clean_str)
    
    if not numbers or not direction_match:
        return 0.0
        
    direction = direction_match.group()
    
    degrees = float(numbers[0]) if len(numbers) > 0 else 0.0
    minutes = float(numbers[1]) if len(numbers) > 1 else 0.0
    seconds = float(numbers[2]) if len(numbers) > 2 else 0.0
    
    decimal = degrees + (minutes / 60) + (seconds / 3600)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def parse_table(coord_list):
    return [[parse_coordinate(lat), parse_coordinate(lon)] for lat, lon in coord_list]

# --- 2. EXACT DIGITAL TWIN & OFFICIAL PORT DATA ---
pilot_station = [parse_coordinate("35° 18',60 N"), parse_coordinate("003° 09',70 W")]
shoal = [parse_coordinate("35° 19' 14\" N"), parse_coordinate("3° 06' 39\" W")]

# General Port Limits (Roadstead / Rade)
# Appended with landward anchor points to smoothly cover the coastline and port
general_port_limits_raw = [
    ["35° 13' 26\" N", "003° 13' 17\" W"], # R1 (West boundary)
    ["35° 14' 12\" N", "003° 16' 00\" W"], # R2 (Seaward West)
    ["35° 21' 37\" N", "003° 16' 00\" W"], # R3 (Seaward North-West)
    ["35° 21' 37\" N", "003° 01' 30\" W"], # R4 (Seaward North-East)
    ["35° 13' 00\" N", "003° 01' 30\" W"], # Coastal Anchor East (Closes the polygon over land)
    ["35° 12' 30\" N", "003° 09' 00\" W"]  # Coastal Anchor South (Covers the port inside the bay)
]

# Access Channel (C1 -> C3 -> C5 -> C7 -> C8 -> C6 -> C4 -> C2)
access_channel_raw = [
    ["35° 17' 18\" N", "003° 09' 13\" W"], ["35° 16' 56\" N", "003° 09' 15\" W"],
    ["35° 16' 35\" N", "003° 09' 23\" W"], ["35° 16' 13\" N", "003° 09' 42\" W"],
    ["35° 16' 01\" N", "003° 09' 29\" W"], ["35° 16' 29\" N", "003° 09' 08\" W"],
    ["35° 16' 49\" N", "003° 08' 59\" W"], ["35° 17' 10\" N", "003° 08' 50\" W"] 
]

# Anchorages
west_anchorage_raw = [
    ["35° 14' 56\" N", "003° 15' 49\" W"], ["35° 14' 56\" N", "003° 12' 08\" W"],
    ["35° 16' 38\" N", "003° 12' 08\" W"], ["35° 16' 38\" N", "003° 15' 49\" W"]
]

east_anchorage_raw = [
    ["35° 18' 40\" N", "003° 05' 06\" W"], ["35° 20' 48\" N", "003° 03' 07\" W"],
    ["35° 21' 29\" N", "003° 03' 51\" W"], ["35° 19' 22\" N", "003° 05' 50\" W"]
]

# Inner Terminals (Mapped logically relative to C7/C8 with operational depths)
terminal_cont_west_raw = [
    ["35° 15' 55\" N", "003° 09' 40\" W"], ["35° 15' 35\" N", "003° 09' 40\" W"],
    ["35° 15' 35\" N", "003° 09' 20\" W"], ["35° 15' 55\" N", "003° 09' 20\" W"]
]

terminal_cont_east_raw = [
    ["35° 15' 55\" N", "003° 09' 15\" W"], ["35° 15' 35\" N", "003° 09' 15\" W"],
    ["35° 15' 35\" N", "003° 08' 50\" W"], ["35° 15' 55\" N", "003° 08' 50\" W"]
]

terminal_vrac_raw = [
    ["35° 16' 15\" N", "003° 08' 45\" W"], ["35° 15' 58\" N", "003° 08' 45\" W"],
    ["35° 15' 58\" N", "003° 08' 30\" W"], ["35° 16' 15\" N", "003° 08' 30\" W"]
]

terminal_hydro_raw = [
    ["35° 16' 30\" N", "003° 09' 50\" W"], ["35° 16' 15\" N", "003° 09' 50\" W"],
    ["35° 16' 15\" N", "003° 09' 42\" W"], ["35° 16' 30\" N", "003° 09' 42\" W"]
]

# Process Arrays
port_limits = parse_table(general_port_limits_raw)
access_channel = parse_table(access_channel_raw)
west_anchorage = parse_table(west_anchorage_raw)
east_anchorage = parse_table(east_anchorage_raw)
term_cont_west = parse_table(terminal_cont_west_raw)
term_cont_east = parse_table(terminal_cont_east_raw)
term_vrac = parse_table(terminal_vrac_raw)
term_hydro = parse_table(terminal_hydro_raw)

# --- 3. INITIALIZE THE MAP & ECDIS PLUGINS ---
port_map = folium.Map(location=[35.2600, -3.1200], zoom_start=11, tiles='CartoDB positron')

port_map.add_child(plugins.MeasureControl(position='topleft', primary_length_unit='nauticalmiles'))
formatter = "function(num) {return L.Util.formatNum(num, 5) + ' º ';};"
plugins.MousePosition(
    position='topright', separator=' | ', empty_string='NaN', lng_first=False,
    num_digits=5, prefix='Cursor:', lat_formatter=formatter, lng_formatter=formatter,
).add_to(port_map)
plugins.Draw(export=True, position='topleft').add_to(port_map)

# --- 4. DRAW THE MARITIME LAYERS ---
# General Port Limits (Roadstead / Rade)
folium.Polygon(
    locations=port_limits, color='blue', weight=1, fill=True, fill_opacity=0.08, 
    popup='<b>General Port Limits (Roadstead)</b><br>Encompassing Betoya Bay'
).add_to(port_map)

# Anchorages
folium.Polygon(locations=west_anchorage, color='magenta', weight=2, fill=True, fill_opacity=0.15, popup='<b>West Anchorage</b><br>Limits: MW1 - MW4').add_to(port_map)
folium.Polygon(locations=east_anchorage, color='magenta', weight=2, fill=True, fill_opacity=0.15, popup='<b>East Anchorage</b><br>Limits: ME1 - ME4').add_to(port_map)

# Access Channel
folium.Polygon(locations=access_channel, color='black', weight=2, fill=True, fill_color='lightblue', fill_opacity=0.4, popup='<b>Access Channel</b><br>Depth: -22.0m').add_to(port_map)

# Terminals
folium.Polygon(locations=term_cont_west, color='green', weight=2, fill=True, fill_opacity=0.5, popup='<b>Container Terminal West</b><br>Depth: -18.0m').add_to(port_map)
folium.Polygon(locations=term_cont_east, color='darkgreen', weight=2, fill=True, fill_opacity=0.5, popup='<b>Container Terminal East</b><br>Depth: -18.0m').add_to(port_map)
folium.Polygon(locations=term_vrac, color='saddlebrown', weight=2, fill=True, fill_opacity=0.5, popup='<b>Terminal Vrac Solide</b><br>Depth: -20.0m').add_to(port_map)
folium.Polygon(locations=term_hydro, color='purple', weight=2, fill=True, fill_opacity=0.5, popup='<b>Hydrocarbon Terminal</b><br>Depth: -22.0m').add_to(port_map)

# Critical Marks
folium.Marker(location=pilot_station, popup="<b>Pilot Boarding Point</b><br>Approx 3NM North of entrance", icon=folium.Icon(color="red", icon="flag")).add_to(port_map)
folium.CircleMarker(location=shoal, radius=6, color="orange", fill=True, fill_color="orange", popup="<b>Isolated Shoal</b><br>Depth: 15m").add_to(port_map)

# --- 5. RENDER IN STREAMLIT ---
st.set_page_config(layout="wide")
st.title("⚓ Nador West Med - ECDIS Passage Planning")
st.markdown("Interactive layout detailing the official roadstead limits, anchorages, access channel, and terminal berths. Use the drawing toolbar to plot tracks and export standard GeoJSON routes.")

st_folium(port_map, width=1200, height=750)
