# Phase 0: Data Preparation

**Goal:** Set up and validate all necessary data sources for InsightAtlas to function smoothly during early development and prototype deployment.

This phase ensures that your core datasets — particularly Canadian Census Tracts (CTs) and optional overlays like Federal Electoral Districts (FEDs) — are clean, consistent, and ready for mapping and analysis.

---

## 1. Core Datasets

### 1.1 CT GeoJSON (`LCT_000B21a_E.geojson`)

- Must include the `CTUID` column (Census Tract Unique Identifier)
- Should contain valid `geometry` for every CT
- Check for:
  - Missing or duplicate CTUIDs
  - Invalid or null geometries
  - Projection consistency (ideally EPSG:4326 for Leaflet/Folium)

### 1.2 CT Indicator CSV (`ct_data.csv`)

- Must include:
  - `CTUID` (matching the GeoJSON)
  - One or more indicator columns (e.g., `under14_pct`, `median_income`)
- Ensure:
  - Clean column names (snake_case recommended)
  - No missing values in the `CTUID` column
  - Proper numeric types for indicator values

---

## 2. Optional Overlay Datasets

### 2.1 FED GeoJSON (`FED_2021_E.geojson`)

- Includes `FEDUID`, `FEDNAME`, and `geometry`
- Should use same CRS as CT layer (or be reprojected)
- Will be added as a secondary map layer in Phase 2

### 2.2 FED Indicator CSV (`fed_data.csv`)

- Optional summary metrics per FED
- Must include a join key: `FEDUID` or `FEDNAME`

---

## 3. File Placement and Naming

Place your working files in the `config/prototype/` folder for Phase 0 testing.

```
config/
└── prototype/
    ├── config.yaml
    ├── ct_data.csv
    ├── LCT_000B21a_E.geojson
    ├── FED_2021_E.geojson        # Optional
    └── fed_data.csv              # Optional
```

> These files should be local only and excluded from version control via `.gitignore`.

---

## 4. Validation Checklist

Use a simple Jupyter notebook or Python script to validate:

- [ ] CT GeoJSON loads and has valid geometries
- [ ] Indicator CSV joins correctly on `CTUID`
- [ ] All indicator columns are numeric and formatted
- [ ] Optional FED files are clean and joinable (if used)

You may want to use `geopandas`, `shapely`, and `pandas` for this phase.

---

## 5. Example CT Indicator CSV Format

```csv
CTUID,under14_pct,median_income,seniors_pct
35100350100,16.4,55800,12.1
35100350200,13.2,61100,14.7
35100350300,17.8,49200,13.4
```

---

## 6. Tips

- Use `geopandas.read_file()` to inspect `.geojson` and validate geometry types
- Keep data clean and minimal for early phases — you can always enrich later
- Avoid including personal data or sensitive information in early datasets

---

## What's Next?

Once data is validated and loaded into your local `config/prototype/` folder, you're ready to move on to **Phase 1: Core CT Dashboard**, where you'll build the first visual choropleth map.
