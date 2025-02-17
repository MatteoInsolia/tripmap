import streamlit as st
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium


APP_TITLE = "Viaggio in Giappone"
APP_SUB_TITLE = "Tappe giorno per giorno"

def main()->None:
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    tappe = pd.DataFrame.from_dict(
        {"Date": ["03-03-2025", "08-03-2025", "28-03-2025"],
        "Description":["Arrivo di Matteo a Hong Kong", "Partenza Da HK per Takamatsu", "Partenza da Tokyo per HK"],
        "Latitude":[22.30331384402351, 34.34206545290941, 35.69666162802782],
        "Longitude":[114.16027652699938, 134.04667994580566, 139.77162061039544]
        }
    ).set_index("Date")

    tappe = gpd.GeoDataFrame(tappe, geometry=gpd.points_from_xy(tappe["Longitude"], tappe["Latitude"]), crs="EPSG:4326")

    map = tappe.explore(tiles="CartoDB positron")

    st_map = st_folium(map, width=700, height=450)



if __name__ == "__main__":
    main()