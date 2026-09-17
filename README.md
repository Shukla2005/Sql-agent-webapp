# 🌤️ Weather Dashboard

A Streamlit weather dashboard that uses the public [Open-Meteo API](https://open-meteo.com/) to display current conditions, a 24-hour temperature and precipitation chart, and a 7-day forecast.

## Features

- Search weather by city name
- Current temperature, feels-like temperature, humidity, wind, and precipitation
- Next-24-hour temperature chart
- Next-24-hour precipitation probability chart
- Seven-day forecast with sunrise and sunset
- No API key or account required
- Cached location and forecast requests for faster reloads

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app is ready to deploy on Streamlit Community Cloud with `app.py` as the entry point.
