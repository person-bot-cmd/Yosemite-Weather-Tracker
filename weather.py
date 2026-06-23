import requests
import pandas as pd
from datetime import date, timedelta

# My camping location
LATITUDE = 37.8651
LONGITUDE = -119.5383
LOCATION_NAME = "Yosemite National Park"

# Camping month and day range (August 1-14)
CAMP_MONTH = 8
CAMP_START_DAY = 1
CAMP_END_DAY = 14

def get_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "America/Los_Angeles",
        "forecast_days": 7
    }
    response = requests.get(url, params=params)
    return response.json()

def get_historical_weather(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "America/Los_Angeles"
    }
    response = requests.get(url, params=params)
    return response.json()

# Convert to DataFrames and combine
dfs = []
for year_data in all_data:
    df = pd.DataFrame({
        "date": year_data["daily"]["time"],
        "max_temp": year_data["daily"]["temperature_2m_max"],
        "min_temp": year_data["daily"]["temperature_2m_min"]
    })
    dfs.append(df)

historical_df = pd.concat(dfs, ignore_index=True)
print(historical_df)

# Run everything
print(f"Weather analysis for {LOCATION_NAME}")
print("=" * 40)

print("\n--- Historical August Averages (last 5 years) ---")
print(historical_df)
print(f"\nAverage High: {historical_df['max_temp'].mean():.1f}°C")
print(f"Average Low: {historical_df['min_temp'].mean():.1f}°C")

print("\n--- 7-Day Forecast ---")
print(forecast_df)

