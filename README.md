# InsightAtlas

**A flexible dashboard for exploring and sharing regional insights through data.**  
InsightAtlas makes it easy to map and compare geographic trends using your own CSV data. Originally created to support community canvassing, the app is built to adapt — whether you're working on education access, public engagement, or local planning.

---

## Overview

InsightAtlas is designed for data scientists, analysts, and civic-minded teams who want to turn data into clear, actionable stories — especially those with a regional focus. With just a few configuration tweaks, you can use it to:

- Prioritize outreach based on local engagement trends
- Map access to education programs or community services
- Understand neighborhood-level metrics and disparities
- Create interactive visual narratives to support decisions or policy

---

## Features

- Customizable regional maps using your own data
- Simple setup for each organization using separate config folders
- Choose which columns to visualize and label
- Modular code that’s easy to read and build on
- Interactive, web-based interface built with Streamlit

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
│   ├── prototype/
│   ├── ct_boundaries.geojson
│   ├── ct_values.csv
│   └── config.yaml      # Optional for later
├── data/                     # Add .gitignore to skip this
├── docs/                     # Developer notes, phase plans, usage guides
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

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Start the app:
   ```
   streamlit run app/main.py
   ```

---

## Use Case Example

InsightAtlas was originally built for a community canvassing team to help them visualize engagement levels across neighborhoods. By adjusting just a few settings, it can now support education groups, nonprofits, local governments, and anyone working with spatial data.

---

## Tech Stack

- Python
- Streamlit
- Pandas
- YAML for configuration
- (Optional) Plotly or Folium for map visuals

---

## Working with Your Data

InsightAtlas keeps your data private. Each setup uses a local CSV and config file that stays on your machine. In future versions, we’ll add support for loading data from the cloud.

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
