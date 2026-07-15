import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap, MarkerCluster
import numpy as np
import os

print("Starting Atlas GIS Pipeline execution...")

# 1. Setup paths and directories
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)
csv_path = os.path.join(data_dir, "repd_cleaned.csv")
geojson_path = os.path.join(data_dir, "repd_atlas_ready.geojson")

# Load data
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"Could not find {csv_path}. Please run ingest_repd.py first!")

df = pd.read_csv(csv_path)

# 2. Coordinate Translation & Geospatial Preparation
# Convert local British National Grid coordinates (EPSG:27700) to Global GPS (EPSG:4326)
gdf = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df['X-coordinate'], df['Y-coordinate']), 
    crs="EPSG:27700"
)
gdf = gdf.to_crs("EPSG:4326")

# 3. ADVANCED LAYER INTEGRATION: Ingest & Mock Curtailment Data
# We simulate BMRS outputs directly into the master GeoDataFrame prior to file export.
# This future-proofs the schema for the Curtailment Data Pipeline contributor.
np.random.seed(42)  # Ensures reproducible mock patterns
gdf['Curtailment_MWh'] = np.random.randint(100, 15000, size=len(gdf))

# Calculate a 1-5 Constraint Score based on curtailment quintiles
# (1 = Low constraint area, 5 = Severe curtailment bottleneck)
gdf['Constraint_Score'] = pd.qcut(gdf['Curtailment_MWh'], 5, labels=[1, 2, 3, 4, 5]).astype(int)

# 4. THE INTEGRATION LAYER: Machine-Readable Export
# Exporting the comprehensive spatial database with queryable properties for other subsystems
gdf.to_file(geojson_path, driver="GeoJSON")
print(f"-> SUCCESS: Integration Layer exported to: {geojson_path}")


# 5. THE PRESENTATION LAYER: Interactive Mapping
uk_map = folium.Map(location=[55.3781, -3.4360], zoom_start=6)

# Instantiate the three toggleable feature groups requested by the brief
capacity_heatmap_layer = folium.FeatureGroup(name="Capacity Heatmap (Generation Density)", show=True)
curtailment_heatmap_layer = folium.FeatureGroup(name="Curtailment Heatmap (Grid Constraints)", show=True)
pin_layer = folium.FeatureGroup(name="Individual Sites (Pins)", show=True)

capacity_heat_data = []
curtailment_heat_data = []
marker_cluster = MarkerCluster().add_to(pin_layer)

# The upgraded "Sorting Hat" Loop
for index, row in gdf.iterrows():
    try:
        lon = row.geometry.x
        lat = row.geometry.y
        capacity = float(row['Installed Capacity (MWelec)']) if pd.notnull(row['Installed Capacity (MWelec)']) else 0.1
        site_name = row['Site Name']
        tech_type = str(row['Technology Type'])
        curtailment = row['Curtailment_MWh']
        score = row['Constraint_Score']
        
        # Build dataset for the Generation Capacity Heatmap
        capacity_heat_data.append([lat, lon, capacity])
        
        # Build dataset for the Grid Constraints Heatmap
        curtailment_heat_data.append([lat, lon, curtailment])
        
        # Color coding based on Technology Type
        if 'Wind' in tech_type:
            pin_color = 'blue'
        elif 'Solar' in tech_type:
            pin_color = 'orange'
        else:
            pin_color = 'green'
            
        # Rich UI Tooltip Popup exposing internal analytics fields
        popup_text = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; width: 220px;">
            <h4 style="margin: 0 0 5px 0; color: #333;">{site_name}</h4>
            <b>Type:</b> {tech_type}<br>
            <b>Capacity:</b> {capacity} MW<br>
            <hr style="margin: 5px 0; border: 0; border-top: 1px solid #ccc;">
            <b style="color: #c0392b;">Estimated Curtailment:</b> {curtailment:,} MWh<br>
            <b>Constraint Rank:</b> <span style="padding: 2px 6px; background-color: #f1c40f; border-radius: 3px; font-weight: bold;">{score}/5</span>
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color=pin_color, icon='info-sign')
        ).add_to(marker_cluster)
        
    except Exception as e:
        continue

# Add the analytical heatmaps to their respective layers
HeatMap(capacity_heat_data, radius=15, blur=10).add_to(capacity_heatmap_layer)
HeatMap(curtailment_heat_data, radius=20, blur=15).add_to(curtailment_heatmap_layer)

# Attach all elements and toggle control to the master layout
capacity_heatmap_layer.add_to(uk_map)
curtailment_heatmap_layer.add_to(uk_map)
pin_layer.add_to(uk_map)
folium.LayerControl(position="topright").add_to(uk_map)

# Update UI Custom HTML Legend to reflect the dual analytical layers cleanly
legend_html = '''
<div style="
    position: fixed; 
    bottom: 40px; left: 40px; width: 190px; height: auto; 
    border: 2px solid #555; z-index: 9999; font-size: 13px; font-family: Arial, sans-serif;
    background-color: white; padding: 12px; border-radius: 6px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    ">
    <b style="font-size:14px; display:block; margin-bottom:8px;">Atlas Layer Key</b>
    
    <i class="fa fa-map-marker fa-lg" style="color:blue; width:15px; text-align:center;"></i> Wind Infrastructure<br>
    <i class="fa fa-map-marker fa-lg" style="color:orange; width:15px; text-align:center;"></i> Solar Infrastructure<br>
    <i class="fa fa-map-marker fa-lg" style="color:green; width:15px; text-align:center;"></i> Other Generation<br>
    
    <hr style="margin: 10px 0; border: 0; border-top: 1px solid #ccc;">
    
    <div style="display:flex; align-items:center; margin-bottom:4px;">
        <span style="background: linear-gradient(to right, blue, lime, yellow, red); display:inline-block; width:50px; height:12px; margin-right:8px; border-radius:2px;"></span> 
        <span style="font-weight:bold;">Heat Gradients</span>
    </div>
    <div style="font-size:11px; color:#555; margin-left: 10px; line-height: 1.5;">
        • Capacity Density<br>
        • Grid Curtailment
    </div>
</div>
'''
uk_map.get_root().html.add_child(folium.Element(legend_html))

# Compile and compile presentation deployment
uk_map.save("index.html")
print("-> SUCCESS: Presentation Layer updated at: index.html")
print("Pipeline run fully complete.")