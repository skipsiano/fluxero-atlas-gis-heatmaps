# --- UPDATED CONFIG TO MATCH YOUR EXACT CSV ---
REQUIRED_COLUMNS = {
    "site_id": "Old Ref ID",           # Or whichever ID column your CSV uses
    "site_name": "Site Name",
    "technology": "Technology Type",
    "capacity_mw": "Installed Capacity (MWelec)",
    "status": "Development Status (short)",
    "longitude": "X-coordinate",       # Pulling your raw British grid data
    "latitude": "Y-coordinate",
}

# (Keep PLACEHOLDER_FIELDS exactly as they are)

def load_cleaned_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

def build_geodataframe(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Rename to a clean schema and perform coordinate translation."""
    rename_map = {v: k for k, v in REQUIRED_COLUMNS.items() if v in df.columns}
    df = df.rename(columns=rename_map)

    # Add placeholder fields so the schema is stable from day one
    for field in PLACEHOLDER_FIELDS:
        df[field] = None

    # Translate British National Grid to Global GPS for the export
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:27700",
    )
    gdf = gdf.to_crs("EPSG:4326")
    
    # Overwrite the old British coordinates with the new GPS ones
    gdf["longitude"] = gdf.geometry.x
    gdf["latitude"] = gdf.geometry.y
    
    return gdf