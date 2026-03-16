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
general_port_limits_raw = [
    ["35° 13' 26\" N", "003° 13' 17\" W"], # R1
    ["35° 14' 12\" N", "003° 16' 00\" W"], # R2
    ["35° 21' 37\" N", "003° 16' 00\" W"], # R3
    ["35° 21' 37\" N", "003° 01' 30\" W"], # R4
    ["35° 13' 00\" N", "003° 01' 30\" W"], # Coastal Anchor East
    ["35° 12' 30\" N", "003° 09' 00\" W"]  # Coastal Anchor South
]

# Access Channel
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

# Process Arrays
port_limits = parse_table(general_port_limits_raw)
access_channel = parse_table(access_channel_raw)
west_anchorage = parse_table(west_anchorage_raw)
east_anchorage = parse_table(east_anchorage_raw)

# --- 3. INITIALIZE THE MAP & SATELLITE TILESET ---
esri_tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
esri_attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'

port_map = folium.Map(
    location=[35.2500, -3.1200], 
    zoom_start=12, 
    tiles=esri_tiles, 
    attr=esri_attr
)

# Essential Planning Tools
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
    locations=port_limits, color='cyan', weight=2, fill=False, fill_opacity=0.0, 
    popup='<b>General Port Limits (Roadstead)</b><br>Encompassing Betoya Bay'
).add_to(port_map)

# Anchorages
folium.Polygon(locations=west_anchorage, color='magenta', weight=2, fill=True, fill_opacity=0.2, popup='<b>West Anchorage</b><br>Limits: MW1 - MW4').add_to(port_map)
folium.Polygon(locations=east_anchorage, color='magenta', weight=2, fill=True, fill_opacity=0.2, popup='<b>East Anchorage</b><br>Limits: ME1 - ME4').add_to(port_map)

# Access Channel
folium.Polygon(locations=access_channel, color='yellow', weight=2, fill=True, fill_color='lightblue', fill_opacity=0.3, popup='<b>Access Channel</b><br>Depth: -22.0m').add_to(port_map)

# Critical Marks
folium.Marker(location=pilot_station, popup="<b>Pilot Boarding Point</b><br>Approx 3NM North of entrance", icon=folium.Icon(color="red", icon="flag")).add_to(port_map)
folium.CircleMarker(location=shoal, radius=6, color="orange", fill=True, fill_color="orange", popup="<b>Isolated Shoal</b><br>Depth: 15m").add_to(port_map)

# --- Custom Drawn Berths from GeoJSON ---
try:
    folium.GeoJson(
        'data (1).geojson',
        name='Inner Berths (Traced)',
        style_function=lambda feature: {
            'color': 'cyan', 
            'weight': 4,
            'opacity': 0.8
        }
    ).add_to(port_map)
except FileNotFoundError:
    pass # Fails silently if the file isn't uploaded yet, preventing app crashes

# --- 5. RENDER IN STREAMLIT ---
st.set_page_config(layout="wide")
st.title("⚓ Nador West Med - ECDIS Passage Planning")
st.markdown("### Interactive Passage Plan Drafting")
st.markdown("Use the drawing toolbar on the left to plot your approach tracks, set waypoints, and export standard GeoJSON routes for simulation and training. The inner berths are loaded from your custom tracing.")

st_folium(port_map, width=1200, height=750)
