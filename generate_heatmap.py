import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap, MarkerCluster
import os

print("Loading cleaned REPD data...")
data_path = os.path.join("data", "repd_cleaned.csv")
df = pd.read_csv(data_path)

operational_df = df[df['Development Status (short)'] == 'Operational'].copy()
print(f"Mapping {len(operational_df)} sites with multiple layers...")

# Convert coordinates
gdf = gpd.GeoDataFrame(
    operational_df, 
    geometry=gpd.points_from_xy(operational_df['X-coordinate'], operational_df['Y-coordinate']),
    crs="EPSG:27700"
)
gdf = gdf.to_crs(epsg=4326)

# Create the base map
uk_map = folium.Map(location=[55.3781, -3.4360], zoom_start=6)

# --- THE FIX: Set both layers to show=True by default ---
heatmap_layer = folium.FeatureGroup(name="Capacity Heatmap (Density)", show=True)
pin_layer = folium.FeatureGroup(name="Individual Sites (Pins)", show=True) 

heat_data = []
marker_cluster = MarkerCluster().add_to(pin_layer)

# Loop through the data once, but add data to both layers
for index, row in gdf.iterrows():
    try:
        lon = row.geometry.x
        lat = row.geometry.y
        capacity = float(row['Installed Capacity (MWelec)']) if pd.notnull(row['Installed Capacity (MWelec)']) else 0.1
        site_name = row['Site Name']
        tech_type = str(row['Technology Type'])
        
        # 1. Prep Heatmap Data
        heat_data.append([lat, lon, capacity])
        
        # --- NEW FLAIR: Color-code the pins based on technology ---
        if 'Wind' in tech_type:
            pin_color = 'blue'
        elif 'Solar' in tech_type:
            pin_color = 'orange'
        else:
            pin_color = 'green'
            
        # 2. Add Pins to the Pin Layer with the custom color icon
        popup_text = f"<b>Site:</b> {site_name}<br><b>Type:</b> {tech_type}<br><b>Capacity:</b> {capacity} MW"
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color=pin_color, icon='info-sign')
        ).add_to(marker_cluster)
        
    except Exception:
        continue

# Render the HeatMap onto its specific layer
HeatMap(heat_data, radius=15, blur=12, max_zoom=10).add_to(heatmap_layer)

# Add both layers to the base map
heatmap_layer.add_to(uk_map)
pin_layer.add_to(uk_map)

# --- THE MAGIC MENU: Add a control box so the user can check/uncheck layers ---
folium.LayerControl().add_to(uk_map)

# --- THE UPGRADE: Inject a custom HTML Legend ---
legend_html = '''
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 130px; height: 110px; 
    border:2px solid grey; z-index:9999; font-size:14px;
    background-color:white; padding: 10px; border-radius: 5px;
    ">
    <b>Energy Type</b><br>
    <i class="fa fa-map-marker fa-1.5x" style="color:blue"></i> Wind<br>
    <i class="fa fa-map-marker fa-1.5x" style="color:orange"></i> Solar<br>
    <i class="fa fa-map-marker fa-1.5x" style="color:green"></i> Other
</div>
'''
uk_map.get_root().html.add_child(folium.Element(legend_html))
# ------------------------------------------------

# Save the final map
uk_map.save("index.html")
print("Success! Layered map with legend generated. Refresh index.html to view.")

uk_map.save("index.html")
print("Success! Layered map generated. Refresh index.html to view.")