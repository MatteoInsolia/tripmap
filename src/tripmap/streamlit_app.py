import streamlit as st


from pathlib import Path
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from dataclasses import dataclass


APP_TITLE = "Viaggio in Giappone"
APP_SUB_TITLE = "Tappe giorno per giorno"

DATA_PATH = Path.cwd() / "data"
POINTS_FILE = "points.json"
ROUTES_FILE = "routes.json"


@dataclass
class TripDataColumns:
    date = "date"
    day = "Giorno"
    description = "Descrizione"
    color = "color"
    geometry = "geometry"


TRIP = TripDataColumns()


def get_trip_data(points_file: Path, routes_file: Path) -> gpd.GeoDataFrame:
    points = gpd.read_file(points_file).set_index(TRIP.date)
    routes = gpd.read_file(routes_file).set_index(TRIP.date)
    return pd.concat([points, routes])


def get_trip_map(trip_data: gpd.GeoDataFrame) -> folium.Map:
    return trip_data.explore(
        color=trip_data[TRIP.color].to_list(),
        tiles="CartoDB positron",
        tooltip=False,
        popup=[TRIP.day, TRIP.description],
        style_kwds=dict(
            style_function=lambda x: {
                "html": f"""<span   class="fa-solid fa-location-dot" 
                                    style="color:{x["properties"][TRIP.color]};
                                    font-size:30px"></span>"""
            },
        ),
        marker_type="marker",
        marker_kwds=dict(icon=folium.DivIcon()),
    )


trip_data = get_trip_data(DATA_PATH / POINTS_FILE, DATA_PATH / ROUTES_FILE)


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=":shinto-shrine:", layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    trip_map = get_trip_map(trip_data)

    st_map = st_folium(trip_map, width=1400, height=700, returned_objects=[])

    st.write(st_map)


if __name__ == "__main__":
    main()
