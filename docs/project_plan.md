# InsightAtlas Project Plan

A modular dashboard to support data-driven storytelling, community engagement, and operational mapping through regional insights — starting with Canadian Census Tracts (CTs) and extending to broader civic use cases.

---

## Overview

InsightAtlas is being developed in phases to ensure clean, scalable growth. Each phase builds on the last, moving from local prototyping to interactive mapping, to real-time team collaboration via cloud sync.

The initial focus is on enabling community canvassing teams to explore demographic indicators and track outreach progress at the Census Tract level, with optional overlays for Federal Electoral Districts (FEDs).

---

## Phase Breakdown

### Phase 0: Data Preparation (Setup)

**Goal:** Ensure input files are clean, complete, and structurally aligned.

#### Requirements:
- [x] `ct_values.csv` with columns like `DGUID`, `age_20to34`, `renting`, `edu_abvBach`, etc.
- [x] `ct_boundaries.geojson` with valid geometries and `DGUID`s
- [ ] Optional: `FED_2021_E.geojson` for overlay support
- [ ] Optional: `fed_data.csv` for FED-level summaries
- [ ] Optional: Backend credentials (for later cloud sync and user access)
- [x] Cloud loading from Google Drive enabled via Streamlit

---

### Phase 1: Core CT Dashboard

**Goal:** Build the foundational map experience using CTs.

#### Subphases:
1. [x] Load CT GeoJSON and render boundaries
2. [x] Join and display CT indicator data
3. [x] Enable dropdown to select indicator for choropleth coloring
4. [x] Add popups (on click) with CT-level stats
5. [x] Ensure map responsiveness and rendering performance on mobile
6. [x] (Bonus) Apply `simplify()` for geometry efficiency and `highlight_function` for map interactivity

---

### Phase 2: FED Overlay Support

**Goal:** Add a secondary layer for orientation, filtering, and grouping.

#### Subphases:
1. [ ] Load and display FED boundaries (as outline layer)
2. [ ] Allow users to select a FED and zoom to it
3. [ ] Filter CTs by selected FED (spatial join or lookup)
4. [ ] (Optional) Show FED-level stats in sidebar
5. [ ] (Planned) Extend configuration support to overlay layers

---

### Phase 3: Local Canvassing Interaction

**Goal:** Allow users to mark CTs as “canvassed” during a local session.

#### Subphases:
1. [ ] Enable marking of CTs via click or toggle
2. [ ] Track canvassed CTs using `st.session_state`
3. [ ] Visually update map to reflect canvassed status
4. [ ] Allow reset or undo
5. [ ] Export canvassed CT list for offline use

---

### Phase 4: Cloud Sync + Access Control

**Goal:** Centralize canvassing progress and support user-based views.

#### Subphases:
1. [ ] Connect to a backend (Firebase, Supabase, etc.)
2. [ ] Sync canvassed CTs in real-time
3. [ ] Load previously canvassed data on launch
4. [ ] Add visibility controls (e.g., “show only mine”)
5. [ ] Optional: Auth system to manage users and access

---

## Supporting Files

### Requirements

**requirements.txt**
- `streamlit`, `pandas`, `geopandas`, `folium`, `streamlit-folium`, `requests`, `shapely`, `protobuf<4.0`

**packages.txt** (for Streamlit Cloud)
- `gdal`, `geos`, `proj-bin`

---

## Design Principles

- [x] Each phase is cleanly layered to minimize refactoring
- [x] Geographic data joins use stable IDs (`DGUID`, `FEDUID`)
- [x] Interactivity is local-first, then scaled to cloud
- [x] Cloud-based files use Google Drive with toggleable local fallback
- [x] Code is modular, with folders for `map_logic`, `interaction`, and `utils`
- [x] Designed to support multiple organizations with isolated configs

---

## Future Enhancements (Post-MVP)

- [ ] Export-ready PDF or PNG reports
- [ ] Support for school zones, municipal wards, or other region types
- [ ] Data upload or config wizard UI
- [ ] Accessibility and localization (e.g., French/English toggle)
- [ ] Theming support for civic or educational orgs
