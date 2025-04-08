# Phase 0: Data Preparation

**Goal:** Set up and validate all necessary data sources for InsightAtlas to function smoothly during early development and prototype deployment.

This phase ensures that your core datasets — particularly Canadian Census Tracts (CTs) and optional overlays like Federal Electoral Districts (FEDs) — are clean, consistent, and ready for mapping and analysis.

---

## 1. Core Datasets

### 1.1 CT GeoJSON (`ct_boundaries.geojson`)

- [x] Includes the `DGUID` column (used as the unique join key)
- [x] Contains valid `geometry` for every CT
- [x] Handles:
  - Invalid geometries via `buffer(0)`
  - Missing/null geometries via filtering
  - Reprojection to `EPSG:4326`
  - Simplification for rendering performance

### 1.2 CT Indicator CSV (`ct_values.csv`)

- [x] Includes `DGUID` (to match GeoJSON)
- [x] Contains multiple indicator columns:
  - `age_20to34`, `renting`, `edu_abvBach`, etc.
- [x] All columns use clean `snake_case` format
- [x] No missing values in `DGUID`
- [x] Indicator values are numeric and ready for choropleth mapping

---

## 2. Optional Overlay Datasets

### 2.1 FED GeoJSON (`FED_2021_E.geojson`)

- [ ] Not yet included
- [ ] Will include `FEDUID`, `FEDNAME`, `geometry`
- [ ] Should be reprojected to `EPSG:4326` if used

### 2.2 FED Indicator CSV (`fed_data.csv`)

- [ ] Not yet included
- [ ] Should include `FEDUID` or `FEDNAME` as join key
- [ ] Optional summary-level metrics per riding

---

## 3. File Placement and Naming

Phase 0 uses `config/prototype/` for local development.  
For cloud deployment, files are dynamically downloaded into `data/cloud/` from Google Drive.

```
config/
└── prototype/
    ├── ct_boundaries.geojson
    ├── ct_values.csv
    ├── validate_geojson.py
    └── config.yaml            # Optional for future phases

data/
└── cloud/
    ├── ct_boundaries.geojson
    └── ct_values.csv
```

> Local files are excluded from version control via `.gitignore`. Google Drive links are used for production deployment.

---

## 4. Validation Checklist

Data validation completed using `main.py` and supporting scripts:

- [x] CT GeoJSON loads and has valid geometries
- [x] Indicator CSV joins correctly on `DGUID`
- [x] All indicator columns are numeric and formatted
- [x] Simplified geometry improves performance
- [ ] FED files will be validated in Phase 2

Tools used: `geopandas`, `shapely`, `pandas`, `requests`

---

## 5. Example CT Indicator CSV Format

```csv
DGUID,age_20to34,renting,viz_minority,edu_abvBach
2021S05075350011.02,69.2,62.9,55.8,65.2
2021S05075350011.03,58.4,49.7,42.1,53.5
...
```

---

## 6. Tips

- Use `geopandas.read_file()` to inspect `.geojson` and validate projection
- Cache cloud downloads with `@st.cache_data` to reduce wait time
- Keep early files small and scoped — scale later
- Avoid committing raw data files directly to GitHub

---

## What's Next?

With Phase 0 complete, you're ready to move on to **Phase 1: Core CT Dashboard**, which enables:
- Live map rendering using Folium
- Dynamic metric selection via Streamlit sidebar
- Hover/click interactions for CT-level context