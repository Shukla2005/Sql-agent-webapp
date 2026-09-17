from datetime import datetime

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤️", layout="wide")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Drizzle", "🌦️"),
    55: ("Heavy drizzle", "🌧️"),
    61: ("Light rain", "🌧️"),
    63: ("Rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Light snow", "🌨️"),
    73: ("Snow", "❄️"),
    75: ("Heavy snow", "❄️"),
    80: ("Rain showers", "🌦️"),
    81: ("Rain showers", "🌦️"),
    82: ("Heavy showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with hail", "⛈️"),
}


def weather_label(code: int) -> tuple[str, str]:
    return WEATHER_CODES.get(code, ("Unknown conditions", "🌡️"))


@st.cache_data(ttl=3600, show_spinner=False)
def find_location(query: str) -> dict | None:
    response = requests.get(
        GEOCODING_URL,
        params={"name": query, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    return results[0] if results else None


@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(latitude: float, longitude: float) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "auto",
        "forecast_days": 7,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "is_day,precipitation,weather_code,wind_speed_10m,wind_direction_10m"
        ),
        "hourly": "temperature_2m,precipitation_probability,weather_code",
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "sunrise,sunset,precipitation_probability_max"
        ),
    }
    response = requests.get(FORECAST_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("🌤️ Weather Dashboard")
st.caption("Live forecasts powered by the free Open-Meteo weather API — no API key required.")

with st.sidebar:
    st.header("📍 Location")
    city_query = st.text_input("Search for a city", value="New Delhi")
    search = st.button("Get weather", type="primary", use_container_width=True)
    st.divider()
    st.caption("Data source: Open-Meteo (open-meteo.com)")

if "location" not in st.session_state:
    st.session_state.location = None
if "weather" not in st.session_state:
    st.session_state.weather = None

if search or st.session_state.location is None:
    if not city_query.strip():
        st.warning("Enter a city name to view its weather.")
        st.stop()
    try:
        with st.spinner("Finding location..."):
            location = find_location(city_query.strip())
        if not location:
            st.error("Location not found. Try a city name, such as London or Mumbai.")
            st.stop()
        with st.spinner("Loading forecast..."):
            weather = fetch_weather(location["latitude"], location["longitude"])
        st.session_state.location = location
        st.session_state.weather = weather
    except requests.RequestException:
        st.error("The weather service is temporarily unavailable. Please try again.")
        st.stop()

location = st.session_state.location
weather = st.session_state.weather
current = weather["current"]
units = weather["current_units"]
condition, icon = weather_label(current["weather_code"])
place = ", ".join(filter(None, [location.get("name"), location.get("country")]));

st.subheader(f"{place}  {icon}")
st.caption(f"Updated {datetime.now().strftime('%d %b %Y, %H:%M')} · {condition}")

metric_columns = st.columns(5)
metric_columns[0].metric("Temperature", f"{current['temperature_2m']:.0f}{units['temperature_2m']}")
metric_columns[1].metric("Feels like", f"{current['apparent_temperature']:.0f}{units['apparent_temperature']}")
metric_columns[2].metric("Humidity", f"{current['relative_humidity_2m']}{units['relative_humidity_2m']}")
metric_columns[3].metric("Wind", f"{current['wind_speed_10m']:.0f} {units['wind_speed_10m']}")
metric_columns[4].metric("Precipitation", f"{current['precipitation']}{units['precipitation']}")

st.divider()

hourly = pd.DataFrame(weather["hourly"])
hourly["time"] = pd.to_datetime(hourly["time"])
next_hours = hourly.head(24).copy().set_index("time")
next_hours = next_hours.rename(columns={"temperature_2m": "Temperature", "precipitation_probability": "Rain chance"})

left, right = st.columns([2, 1])
with left:
    st.subheader("Next 24 hours")
    st.line_chart(next_hours[["Temperature"]], y_label=f"Temperature ({units['temperature_2m']})")
with right:
    st.subheader("Rain probability")
    st.bar_chart(next_hours[["Rain chance"]], y_label="Probability (%)")

st.subheader("7-day forecast")
daily = pd.DataFrame(weather["daily"])
daily["date"] = pd.to_datetime(daily.pop("time"))
daily["condition"] = daily["weather_code"].map(lambda code: f"{weather_label(code)[1]} {weather_label(code)[0]}")
daily["day"] = daily["date"].dt.strftime("%a, %d %b")
daily = daily.rename(
    columns={
        "temperature_2m_max": "High",
        "temperature_2m_min": "Low",
        "precipitation_probability_max": "Rain chance",
        "sunrise": "Sunrise",
        "sunset": "Sunset",
    }
)
st.dataframe(
    daily[["day", "condition", "High", "Low", "Rain chance", "Sunrise", "Sunset"]],
    column_config={
        "High": st.column_config.NumberColumn(format=f"%.0f {units['temperature_2m_max']}"),
        "Low": st.column_config.NumberColumn(format=f"%.0f {units['temperature_2m_min']}"),
        "Rain chance": st.column_config.NumberColumn(format="%d%%"),
    },
    hide_index=True,
    use_container_width=True,
)
