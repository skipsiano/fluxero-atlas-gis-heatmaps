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

# --- THE UPGRADE: Create separate toggleable layers ---
heatmap_layer = folium.FeatureGroup(name="Capacity Heatmap (Density)")
pin_layer = folium.FeatureGroup(name="Individual Sites (Pins)", show=False) # show=False hides it by default

heat_data = []
marker_cluster = MarkerCluster().add_to(pin_layer)

# Loop through the data once, but add data to both layers
for index, row in gdf.iterrows():
    try:
        lon = row.geometry.x
        lat = row.geometry.y
        capacity = float(row['Installed Capacity (MWelec)']) if pd.notnull(row['Installed Capacity (MWelec)']) else 0.1
        site_name = row['Site Name']
        tech_type = row['Technology Type']
        
        # 1. Prep Heatmap Data
        heat_data.append([lat, lon, capacity])
        
        # 2. Add Pins to the Pin Layer
        popup_text = f"<b>Site:</b> {site_name}<br><b>Type:</b> {tech_type}<br><b>Capacity:</b> {capacity} MW"
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300)
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

uk_map.save("index.html")
print("Success! Layered map generated. Refresh index.html to view.")