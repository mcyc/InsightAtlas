import streamlit as st
import geopandas as gpd
import pandas as pd
from pathlib import Path
import requests

@st.cache_data
def load_geojson(path):
    """
    Load and preprocess a GeoJSON file.

    Parameters
    ----------
    path : str
        Path to the GeoJSON file.

    Returns
    -------
    gdf : geopandas.GeoDataFrame or None
        Loaded and cleaned GeoDataFrame, or None if loading fails.
    logs : list of str
        Log messages about geometry fixing or reprojection steps.
    """
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
    """
    Load census tract data from a CSV file.

    Parameters
    ----------
    path : str
        Path to the CSV file.

    Returns
    -------
    df : pandas.DataFrame or None
        Loaded DataFrame, or None if reading fails.
    """
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Failed to load CT values CSV: {e}")
        return None

def download_from_gdrive(url, dest_path):
    """
    Download a file from a Google Drive link if it doesn't already exist.

    Parameters
    ----------
    url : str
        Direct download link from Google Drive (e.g. using `uc?export=download`).
    dest_path : str or Path
        Local destination file path.

    Returns
    -------
    path : str or None
        Path to the downloaded file, or None if download failed.
    """
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
