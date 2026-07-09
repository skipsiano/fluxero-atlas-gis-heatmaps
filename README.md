\# REPD GIS Heatmap Subsystem



\*\*Technical Summary\*\*

The REPD GIS Heatmap subsystem is an automated Python pipeline that ingests UK government renewable energy data, translates British National Grid coordinates into standard GPS, and generates a layered, interactive Folium map to identify optimal infrastructure routing zones.



\*\*Integration Specification\*\*

\* \*\*Inputs:\*\* REPD raw CSV data (UK Gov), pandas data structures.

\* \*\*Outputs:\*\* Cleaned geospatial dataset (`repd\_cleaned.csv`), Interactive HTML map (`index.html`) featuring capacity heatmaps and categorised pin layers.

\* \*\*Dependencies:\*\* pandas, geopandas, folium (full list in `requirements.txt`).

\* \*\*Integration Notes:\*\* This subsystem acts as a standalone visualisation layer. For integration into the wider Atlas platform, the `index.html` output can be embedded via an iframe into a web dashboard, or the core GeoDataFrame can be passed directly to Atlas's primary spatial database.



\*\*Deployment Instructions\*\*

1\. Clone the repository.

2\. Create a virtual environment and run: `pip install -r requirements.txt`

3\. Run the map generator: `python generate\_heatmap.py`

