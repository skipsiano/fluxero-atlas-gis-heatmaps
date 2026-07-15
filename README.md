\# REPD GIS Heatmap Subsystem



\*\*Technical Summary\*\*

The REPD GIS Heatmap subsystem is an automated Python pipeline that ingests UK government renewable energy data, translates British National Grid coordinates into standard GPS, and generates a layered, interactive Folium map to identify optimal infrastructure routing zones.



\*\*Integration Specification\*\*

\* \*\*Inputs:\*\* REPD raw CSV data (UK Gov), pandas data structures.

* **Outputs:** 1. `index.html` (Presentation Layer): Interactive, triple-layered diagnostic mapping engine featuring capacity heatmaps, grid constraint overlays, and color-coded generation asset pins with integrated analytics popups.
  2. `data/repd_atlas_ready.geojson` (Integration Layer): Machine-readable spatial database for downstream consumption (Site Ranking Engine, FastAPI endpoints). Contains queryable properties: `Site Name`, `Technology Type`, `Installed Capacity (MWelec)`, `Curtailment_MWh`, and `Constraint_Score`.

\* \*\*Dependencies:\*\* pandas, geopandas, folium (full list in `requirements.txt`).

\* \*\*Integration Notes:\*\* This subsystem acts as a standalone visualisation layer. For integration into the wider Atlas platform, the `index.html` output can be embedded via an iframe into a web dashboard, or the core GeoDataFrame can be passed directly to Atlas's primary spatial database.



\*\*Deployment Instructions\*\*

1\. Clone the repository.

2\. Create a virtual environment and run: `pip install -r requirements.txt`

3\. Run the map generator: `python generate\_heatmap.py`

