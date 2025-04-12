import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path
import requests
from shapely.geometry import GeometryCollection

from core.maplayers import add_custom_choropleth

APP_VERSION = "v0.2.0-dev1"
st.set_page_config(page_title="InsightAtlas | Canadian Demographic Explorer", layout="wide")
st.sidebar.caption(f"Version: {APP_VERSION}")
st.subheader("Census Tracts 2021")

# --- Configuration ---
use_cloud_data = True
CLOUD_DATA_DIR = "data/cloud"
CLOUD_CSV_URL = "https://drive.google.com/uc?export=download&id=1ERHEMcBhyPcgYq2r5iwxEO9KIH45TAN7"
CLOUD_GEOJSON_URL = "https://drive.google.com/uc?export=download&id=1galoO4I9wobrq0lo-ojPCKg0B6ZHrlob"

# default zoom
zoom_start = 9.4

def download_from_gdrive(url, dest_path):
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if not dest_path.exists():
        status = st.empty()
        status.info(f"Downloading {dest_path.name}...")
        r = requests.get(url)
        if r.status_code == 200 and "text/html" not in r.headers.get("Content-Type", ""):
            dest_path.write_bytes(r.content)
        else:
            status.empty()
            st.error(f"Download failed or invalid format for {dest_path.name}")
            return None
        status.empty()
    return str(dest_path)

if use_cloud_data:
    GEOJSON_PATH = download_from_gdrive(CLOUD_GEOJSON_URL, f"{CLOUD_DATA_DIR}/ct_boundaries.geojson")
    CSV_PATH = download_from_gdrive(CLOUD_CSV_URL, f"{CLOUD_DATA_DIR}/ct_values.csv")
else:
    GEOJSON_PATH = "config/prototype/ct_boundaries.geojson"
    CSV_PATH = "config/prototype/ct_values.csv"

JOIN_KEY = "DGUID"
unit = "(Pop. %)"
METRICS = {
    f"Age 20-34 {unit}": "age_20to34",
    f"Renting {unit}": "renting",
    f"Visible Minority {unit}": "viz_minority",
    f"Bachelor's or higher {unit}": "edu_abvBach",
    f"Immigrated in 2016-2021 {unit}": "immigrated_af2016"
}

@st.cache_data
def load_geojson(path):
    logs = []
    try:
        gdf = gpd.read_file(path)
        if (~gdf.geometry.is_valid).sum() > 0:
            logs.append("Fixed invalid geometries using buffer(0).")
            gdf["geometry"] = gdf["geometry"].buffer(0)
        if gdf.crs and gdf.crs.to_string() != "EPSG:4326":
            logs.append(f"Reprojected from {gdf.crs} to EPSG:4326.")
            gdf = gdf.to_crs(epsg=4326)
        gdf["geometry"] = gdf["geometry"].simplify(0.0001, preserve_topology=True)
        return gdf, logs
    except Exception as e:
        st.error(f"Failed to load GeoJSON: {e}")
        return None, []

@st.cache_data
def load_ct_values(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Failed to load CT values CSV: {e}")
        return None

# --- Load and merge ---
gdf, logs = load_geojson(GEOJSON_PATH)
df = load_ct_values(CSV_PATH)

if gdf is not None and df is not None:
    df = df[[JOIN_KEY] + list(METRICS.values())].copy()
    gdf = gdf[gdf[JOIN_KEY].isin(df[JOIN_KEY])]
    gdf = gdf.merge(df, on=JOIN_KEY, how="left")

    # --- Sidebar selection ---
    selected_label = st.sidebar.selectbox("Select metric to visualize:", list(METRICS.keys()))
    selected_metric = METRICS[selected_label]

    # --- Compute center ---
    unioned = gdf.geometry.union_all()
    if isinstance(unioned, GeometryCollection):
        parts = [geom for geom in unioned.geoms if geom.area > 0]
        centroid = GeometryCollection(parts).centroid if parts else unioned.centroid
    else:
        centroid = unioned.centroid
    center = [centroid.y, centroid.x]

    # --- Base map ---
    base_map = folium.Map(location=center, zoom_start=zoom_start, tiles="cartodbpositron")

    # --- Add each metric as a separate (exclusive) base layer ---
    fg_dict = {}
    for label, metric in METRICS.items():
        choropleth, colorbar = add_custom_choropleth(
            fmap=None,
            gdf=gdf,
            value_column=metric,
            popup_fields=["CTNAME", metric],
            popup_aliases=["Tract:", label],
            legend_caption=label,
        )
        fg = folium.FeatureGroup(name=label, overlay=True)  # Treat as overlay
        if colorbar:
            fg.add_child(colorbar)
        fg.add_child(choropleth)
        fg_dict[label]=fg

    # --- Display map in Streamlit ---
    st_folium(
        base_map,
        feature_group_to_add=fg_dict[selected_label],
        height=600,
        use_container_width=True,
        returned_objects=[],
        key="map"
    )

    # --- Optional debug section ---
    with st.expander("Logs and diagnostics"):
        if logs:
            for msg in logs:
                st.info(msg)
        st.dataframe(gdf[[JOIN_KEY, "CTNAME", selected_metric]].head())
else:
    st.warning("Unable to load or render CT boundaries.")
