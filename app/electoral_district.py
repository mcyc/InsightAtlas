import streamlit as st
import folium
from streamlit_folium import st_folium

from core.maplayers import add_custom_choropleth
from utils.map_utils import compute_map_view
from utils.data_loader import load_geojson, download_from_gdrive,\
    load_geojson_from_parquet, load_parquet

APP_VERSION = "v0.4.0.dev5"
st.set_page_config(page_title="InsightAtlas | Canadian Demographic Explorer", layout="wide")
st.sidebar.caption(f"Version: {APP_VERSION}")
st.subheader("Census 2021 - Dissemination Areas")

# --- Configuration ---
table_file = "census_2021_combined.parquet"
geojson_file = "DA_boundaries.parquet"
geojson_file2 = "FED_ED_boundaries_2023.parquet"

use_cloud_data = True
CLOUD_DATA_DIR = "data/cloud"
gcloud_root = "https://drive.google.com/uc?export=download&id="
CLOUD_CSV_URL = f"{gcloud_root}1feWg-8hir4OmMChixJF59OLDkGoroIsK"
CLOUD_GEOJSON_URL = f"{gcloud_root}1cpnwtFmsH-9xypp55JVxfoRjH86_R3Dl"
CLOUD_GEOJSON_URL_2 = f"{gcloud_root}1M5o82kpwWLTCDXr8Ld-4bOKknvxKUIwk"

if use_cloud_data:
    TABLE_PATH = download_from_gdrive(CLOUD_CSV_URL, f"{CLOUD_DATA_DIR}/{table_file}")
    GEOJSON_PATH = download_from_gdrive(CLOUD_GEOJSON_URL, f"{CLOUD_DATA_DIR}/{geojson_file}")
    GEOJSON_PATH_2 = download_from_gdrive(CLOUD_GEOJSON_URL_2, f"{CLOUD_DATA_DIR}/{geojson_file2}")

else:
    workdir = "data/local"
    TABLE_PATH = f"{workdir}/{table_file}"
    GEOJSON_PATH = f"{workdir}/{geojson_file}"
    GEOJSON_PATH_2 = f"{workdir}/{geojson_file2}"

JOIN_KEY = "DGUID"
ED_KEY = "ED_NAMEE"
unit = "(Pop. %)"
METRICS = {
    f"Priority Score": "Priority_Score",
    f"Age 20-34 {unit}": "age_20to34",
    f"Renting {unit}": "renting",
    f"Visible Minority {unit}": "viz_minority",
    f"Bachelor's or higher {unit}": "edu_abvBach",
    f"Immigrated in 2016-2021 {unit}": "immigrated_af2016"
}

# any aditional columns to add to the joint table
columns_others = ['DAUID']

logs = []
# --- Load and merge ---
gdf2, logs = load_geojson(GEOJSON_PATH_2)
df = load_parquet(TABLE_PATH)

if df is not None:
    df = df[[JOIN_KEY] + list(METRICS.values()) + columns_others].copy()

    # --- Electoral district selections ---
    default_ed = "Vancouver Centre"
    #ed_list = ["Vancouver Centre", "Vancouver Granville", "Victoria", "Toronto Centre"]
    ed_list = sorted(gdf2[ED_KEY].dropna().unique())
    # if the default isn't in the table, select the first metro available
    if default_ed not in ed_list:
        default_ed = ed_list[0]

    selected_ed = st.sidebar.selectbox("Select federal electoral district:", ed_list, key="selected_ed",
                                       index=ed_list.index(default_ed), help="Tip: you can use this like a search bar too")

    # --- Sidebar metric selection ---
    selected_label = st.sidebar.selectbox("Select metric:", list(METRICS.keys()), key="selected_label")
    selected_metric = METRICS[selected_label]

    gdf2_selected = gdf2[gdf2[ED_KEY] == selected_ed]

    gdf = load_geojson_from_parquet(
        parquet_path=GEOJSON_PATH,
        labe_ref=selected_ed,
        _geojson_df=gdf2_selected,
        _subset=['DGUID'] #'DAUID',
    )

    # --- Compute center ---
    center, zoom_start = compute_map_view(gdf2_selected)

    # --- Base map ---
    base_map = folium.Map(location=center, zoom_start=zoom_start, tiles="cartodbpositron")

    # 1. Check both have the JOIN_KEY column
    assert JOIN_KEY in gdf.columns, f"{JOIN_KEY} not in gdf"
    assert JOIN_KEY in df.columns, f"{JOIN_KEY} not in df_da"

    # 2. Inner join gdf and df on JOIN_KEY
    gdf[JOIN_KEY] = gdf[JOIN_KEY].astype(str)
    df[JOIN_KEY] = df[JOIN_KEY].astype(str)

    gdf = gdf.merge(df, on=JOIN_KEY, how="inner")

    # --- Add each metric as a separate (exclusive) base layer ---
    fg_dict = {}
    colorbars = {}
    for label, metric in METRICS.items():
        # --- Filter and join data ---

        # specify the popup info
        popup_fields = ['DAUID', metric]  # JOIN_KEY,
        popup_aliases = ["ID:", "Value:"]

        # Add ED boundary overlay
        choropleth_bg = folium.GeoJson(
            gdf2_selected,
            name="ED Boundaries",
            style_function=lambda feature: {
                "fillColor": None,
                "color": "dimgrey",
                "weight": 3,
                "fillOpacity": 0.0,
                "dashArray": "2, 10",
            },
            tooltip=folium.GeoJsonTooltip(fields=["ED_NAMEE"], aliases=["ED:"]),
            lazy=True,
        )

        choropleth, colorbar = add_custom_choropleth(
            fmap=None,
            gdf=gdf,
            value_column=metric,
            linewidth=1,
            popup_fields=popup_fields,
            popup_aliases=popup_aliases
        )
        fg = folium.FeatureGroup(name=label, overlay=True)

        if colorbar:
            colorbars[label] = colorbar

        fg.add_child(choropleth_bg)
        fg.add_child(choropleth)

        fg_dict[label] = fg

    # --- Display map ---
    st.markdown(f"""
    <div>
      <h4 style='font-size: 1rem; margin-top: -1.3rem; margin-bottom:
       -1.5rem; opacity: 0.8;'>{selected_label} - {selected_ed} </h4>
    </div>
    """, unsafe_allow_html=True)

    st_folium(
        base_map,
        feature_group_to_add=fg_dict[selected_label],
        height=600,
        use_container_width=True,
        returned_objects=[],
        key="map"
    )

    # --- Show colorbar ---
    legend_html = colorbars[selected_label]._repr_html_()
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: flex-end;
            padding-right: 10px;
            margin-top: -650px;
        ">
            <div style="
                padding: 6px;
                border-radius: 4px;
                max-width: 100%;
            ">
                {legend_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Optional debug section ---
    with st.expander("Logs and diagnostics"):
        if logs:
            for msg in logs:
                st.info(msg)
else:
    st.warning("Unable to load or render CT boundaries.")
