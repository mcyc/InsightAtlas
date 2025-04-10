# InsightAtlas

[![Streamlit App](https://img.shields.io/badge/Live%20Demo-Streamlit-brightgreen?logo=streamlit)](https://insight-atlas.streamlit.app)
[![Phase](https://img.shields.io/badge/Phase-0%20Complete-blueviolet)](docs/phase_0_data-prep.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](LICENSE)


**A flexible dashboard for exploring and sharing geographical insights through data.**  
InsightAtlas makes it easy to map and compare geographic trends using your own CSV data. Originally created to support community canvassing, the app is built to adapt — whether you're working on education access, public engagement, or local planning.

---

## Overview

InsightAtlas is designed for data scientists, analysts, and civic-minded teams who want to turn data into clear, actionable stories — especially those with a regional focus. With just a few configuration tweaks, you can use it to:

- Prioritize outreach based on local engagement trends
- Map access to education programs or community services
- Understand neighborhood-level metrics and disparities
- Create interactive visual narratives to support decisions or policy
- Deliver lightweight tools for field teams and non-technical users

---

## Features

- Interactive choropleth maps built from your data
- Choose which columns to visualize via dropdown
- Supports local or cloud-hosted data (e.g., Google Drive)
- Mobile-friendly interface powered by Streamlit and Folium
- Modular layout to support multi-phase development
- Built-in tools for data validation, map layering, and future sync

---

## Live Demo

Try the prototype on Streamlit Cloud:  
**→ [Launch InsightAtlas](https://insight-atlas.streamlit.app)**
*(Uses Google Drive to load demo data — no installation required.)*

---

## Project Structure

```
InsightAtlas/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── map_logic/
│   │   ├── ct_layer.py
│   │   ├── fed_overlay.py
│   ├── interaction/
│   │   ├── session_canvassing.py
│   │   └── cloud_sync.py
│   └── utils/
│       ├── data_loader.py
│       ├── spatial_utils.py
│       └── config_parser.py
├── config/
│   └── prototype/
│       ├── ct_boundaries.geojson      # only exists locally
│       ├── ct_values.csv              # only exists locally
│       └── validate_geojson.py
│   └── config.yaml      # Optional for later
├── data/                # Auto-populated cloud downloads (gitignored)
├── docs/
│   ├── project_plan.md
│   ├── phase_0_data-prep.md
│   └── phase_1_core-map.md
├── requirements.txt
├── packages.txt
└── README.md
```

---

## Getting Started

To run InsightAtlas locally:

1. Clone the repo:
   ```
   git clone https://github.com/yourusername/InsightAtlas.git
   cd InsightAtlas
   ```

2. (Optional) Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the app:
   ```
   streamlit run app/main.py
   ```

5. (Optional) Toggle `use_cloud_data = True` in `main.py` to pull data from Google Drive.

---

## Use Case Example

InsightAtlas was originally built for a community canvassing team to help visualize engagement levels across neighborhoods. Since then, it has expanded to support:

- Urban policy research
- Access to education mapping
- Health outreach visualization
- Local planning and service delivery

---

## Tech Stack

- Python + Streamlit
- GeoPandas, Pandas, Folium
- Google Drive integration (via `requests`)
- YAML (planned for config files in later phases)

---

## Working with Your Data

InsightAtlas uses either:
- Local `.geojson` and `.csv` files for development
- Or cloud-hosted files (like public Google Drive links) for deployed use

All processing happens client-side — your data stays in your control.

---

## Deployment

InsightAtlas can be deployed instantly on [Streamlit Cloud](https://streamlit.io/cloud) using:

- `app/main.py` as entry point
- `requirements.txt` (Python deps)
- `packages.txt` (system-level geospatial libs)

See the [docs](docs/) folder for project plans, validation tools, and phase documentation.

---

## License

InsightAtlas is open source under the Apache License 2.0. You’re welcome to use, adapt, and share the project — just include attribution.

---

## About the Creator

**Mike Chen, Ph.D.**  
Data Scientist | AI Strategist | Storyteller  
[GitHub](https://github.com/mcyc) | [LinkedIn](https://www.linkedin.com/in/mike-chen-phd/) | [Portfolio](https://mcyc.github.io)

---

## Feedback & Collaboration

InsightAtlas is a work in progress and open to new ideas. If you’d like to contribute or have suggestions, feel free to open an issue or connect on GitHub.
