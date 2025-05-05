import streamlit as st

# Page config
st.set_page_config(page_title="InsightAtlas", layout="wide")  # page_icon="🌐",

# Main content
st.title("Welcome to InsightAtlas")
st.markdown("""
**InsightAtlas** is a flexible dashboard for exploring and sharing geographic insights through data — 
making it easy to map, compare, and communicate spatial trends using your own datasets.

---

### Overview

Designed for data scientists, analysts, and civic-minded teams, InsightAtlas helps turn data into clear, 
actionable stories — especially those with a regional or community focus. Key features include:

- Prioritizing outreach based on local engagement trends  
- Mapping access to education programs or community services  
- Surfacing neighborhood-level metrics and disparities  
- Creating interactive visual narratives to support decisions or policy  
- Delivering lightweight tools for field teams and non-technical users  

---

### Templates

Choose a template to get started:
""")

st.page_link(
    "pages/Electoral_Districts.py",
    label="**Electoral Districts**: for visualizing neighborhood-level insights in a Canadian federal electoral district, at the Dissemination Areas level.",
    icon=":material/travel_explore:",  # or ":material/read_more:" ":material/explore:"
    use_container_width=True
)

st.page_link(
    "pages/Metro_Areas.py",
    label="**Metropolitan Areas**: for visualizing neighborhood-level insights in a Canadian metropolitan area, at the Census Tracts level.",
    icon=":material/map:",
    use_container_width=True
)

st.divider()
st.caption("""Created by Mike Chen ([GitHub](https://github.com/mcyc) |
 [LinkedIn](https://linkedin.com/in/mike-chen-phd))""")

