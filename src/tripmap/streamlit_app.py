import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import geopandas as gpd
from folium import Map, DivIcon
from streamlit_folium import st_folium
from streamlit_calendar import calendar
from dataclasses import dataclass


APP_TITLE = "Viaggio in Giappone"

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


@dataclass
class CalendarCallbackKeys:
    select = "select"
    date_click = "dateClick"
    event_click = "eventClick"
    event = "event"
    start = "start"
    end = "end"

    def __post_init__(self):
        self.selection_keys = [
            self.date_click,
            self.event_click,
            self.select,
        ]


TRIP = TripDataColumns()
CALENDAR_KEYS = CalendarCallbackKeys()


CALENDAR_OPTIONS = {
    "editable": "true",
    "navLinks": "true",
    "selectable": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridDay,dayGridWeek,dayGridMonth",
    },
    "initialDate": "2025-03-04",
    "initialView": "dayGridMonth",
}

events = [
    {
        "title": "Aereo per Takamatsu",
        "start": "2025-03-08T09:25:00",
        "end": "2025-03-08T13:45:00",
    },
    {
        "title": "Aereo per Hong Kong",
        "start": "2025-03-28T14:40:00",
        "end": "2025-03-28T19:25:00",
    },
]


def get_trip_data(points_file: Path, routes_file: Path) -> gpd.GeoDataFrame:
    points = gpd.read_file(points_file).set_index(TRIP.date)
    routes = gpd.read_file(routes_file).set_index(TRIP.date)
    return pd.concat([points, routes]).sort_index()


def get_trip_map(trip_data: gpd.GeoDataFrame) -> Map:
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
        marker_kwds=dict(icon=DivIcon()),
    )


def get_default_date_range(trip_dates: pd.Index) -> tuple[str, str]:
    return trip_dates.min().date(), trip_dates.max().date()


def user_has_selected_days_on_calendar(calendar_state: dict) -> bool:
    return np.any(
        [key in calendar_state.keys() for key in CALENDAR_KEYS.selection_keys]
    )


def get_next_day(time: pd.Timestamp) -> pd.Timestamp:
    return time.replace(day=time.day + 1)


def get_date_range_from_calendar(calendar_state: dict) -> tuple[str, str]:
    [selection_key] = [
        key for key in CALENDAR_KEYS.selection_keys if key in calendar_state.keys()
    ]
    match selection_key:
        case CALENDAR_KEYS.date_click:
            time = pd.Timestamp(calendar_state[selection_key][TRIP.date])
            start_time = end_time = get_next_day(time)
        case CALENDAR_KEYS.event_click:
            start_time = pd.Timestamp(
                calendar_state[selection_key][CALENDAR_KEYS.event][CALENDAR_KEYS.start]
            )
            end_time = pd.Timestamp(
                calendar_state[selection_key][CALENDAR_KEYS.event][CALENDAR_KEYS.end]
            )
        case CALENDAR_KEYS.select:
            start_time = get_next_day(
                pd.Timestamp(calendar_state[selection_key][CALENDAR_KEYS.start])
            )
            end_time = pd.Timestamp(calendar_state[selection_key][CALENDAR_KEYS.end])
    return start_time.date(), end_time.date()


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=":shinto-shrine:", layout="wide")
    st.title(APP_TITLE)
    st.markdown(
        "La mappa interattiva mostra le nostre tappe e spostamenti. "
        "Col calendario potete selezionare una o più date oppure "
        "un evento per visualizzare solo quella finestra temporale."
    )

    trip_data = get_trip_data(DATA_PATH / POINTS_FILE, DATA_PATH / ROUTES_FILE)

    calendar_state = calendar(
        events=events,
        options=CALENDAR_OPTIONS,
        custom_css="""
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        """,
        key="daygrid",
    )

    start_date, end_date = get_default_date_range(trip_data.index)

    if user_has_selected_days_on_calendar(calendar_state):
        start_date, end_date = get_date_range_from_calendar(calendar_state)

    trip_map = get_trip_map(trip_data.loc[start_date:end_date])

    _ = st_folium(trip_map, width=1400, height=700, returned_objects=[])


if __name__ == "__main__":
    main()
