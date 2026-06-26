import requests
import pandas as pd
from datetime import date, timedelta
import os
#os.environ['MPLBACKEND'] = 'Agg'
#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
import requests
import os

HOT_THRESHOLD  = 60   # temporarily low for testing — change to 80 after
COLD_THRESHOLD = 55
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

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

today = date.today()
current_year = today.year

# Collect historical data for the last 5 years
all_data = []

for year in range(current_year - 5, current_year):
    start = date(year, CAMP_MONTH, CAMP_START_DAY)
    end = date(year, CAMP_MONTH, CAMP_END_DAY)
    data = get_historical_weather(LATITUDE, LONGITUDE, start, end)
    all_data.append(data)
    print(f"Fetched data for {year}")

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

forecast_data = get_forecast(LATITUDE, LONGITUDE)
forecast_df = pd.DataFrame({
    "date": forecast_data["daily"]["time"],
    "max_temp": forecast_data["daily"]["temperature_2m_max"],
    "min_temp": forecast_data["daily"]["temperature_2m_min"]
})

def get_current_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "timezone": "America/Los_Angeles"
    }
    response = requests.get(url, params=params)
    return response.json()


#old matplotlib png code that generates static image (dashboard.png) instead of interactive map:
'''
def generate_dashboard():
    print("Dashboard starting...")
    df = pd.read_csv("daily_log.csv", skipinitialspace=True)
    print("CSV loaded")
    df = pd.read_csv("daily_log.csv")
    print(df.columns.tolist())
    #df["datetime"] = pd.to_datetime(df["date"] + " "git  + df["time"])
    df["datetime"] = pd.to_datetime(df["time"])
    df = df.sort_values("datetime")

    #df = pd.read_csv("daily_log.csv", parse_dates=[["date", "time"]])
    #df = df.rename(columns={"date_time": "datetime"})
    df = df.sort_values("datetime")

    fig, ax = plt.subplots(figsize=(10, 5))
    print("Plotting", df["temp_f"].tolist())
    #ax.plot(df["datetime"], df["temp_f"], color="steelblue", linewidth=2, label="Temp (°F)")
    ax.plot(df["datetime"], df["temp_f"], color="steelblue", linewidth=2, 
        marker='o', markersize=5, label="Temp (°F)")

    max_idx = df["temp_f"].idxmax()
    min_idx = df["temp_f"].idxmin()

    ax.scatter(df.loc[max_idx, "datetime"], df.loc[max_idx, "temp_f"],
               color="red", zorder=5, label=f"Max: {df.loc[max_idx, 'temp_f']}°F")
    ax.scatter(df.loc[min_idx, "datetime"], df.loc[min_idx, "temp_f"],
               color="blue", zorder=5, label=f"Min: {df.loc[min_idx, 'temp_f']}°F")

    ax.annotate(f"Max: {df.loc[max_idx, 'temp_f']}°F",
            xy=(df.loc[max_idx, "datetime"], df.loc[max_idx, "temp_f"]),
            xytext=(10, 10), textcoords="offset points",
            color="red", fontsize=9)

    ax.annotate(f"Min: {df.loc[min_idx, 'temp_f']}°F",
            xy=(df.loc[min_idx, "datetime"], df.loc[min_idx, "temp_f"]),
            xytext=(10, -15), textcoords="offset points",
            color="blue", fontsize=9)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
    plt.xticks(rotation=45)
    ax.set_title("My City Temperature Dashboard")
    ax.set_ylabel("Temperature (°F)")
    ax.legend()
    ax.set_ylim(df["temp_f"].min() - 5, df["temp_f"].max() + 8)
    plt.tight_layout()
    plt.savefig("dashboard.png", dpi=150)
    plt.close()
'''
print("\n--- 7-Day Forecast ---")
print(forecast_df)

historical_df.to_csv("historical_weather.csv", index=False)
forecast_df.to_csv("forecast_weather.csv", index=False)
print("\nData saved to CSV files.")

# Fetch and log today's current temperature
current_data = get_current_weather(LATITUDE, LONGITUDE)
current_temp = current_data["current"]["temperature_2m"]
current_time = current_data["current"]["time"]

temp_c = current_temp  # rename for clarity
temp_f = round(temp_c * 9/5 + 32, 1)
def send_discord_alert(message):
    if not DISCORD_WEBHOOK_URL:
        print("No Discord webhook configured.")
        return
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    if response.status_code == 204:
        print("Discord alert sent.")
    else:
        print(f"Discord alert failed: {response.status_code}")
        
if temp_f > HOT_THRESHOLD:
    send_discord_alert(f"🌡️ Heat alert! {temp_f}°F — above your {HOT_THRESHOLD}°F threshold.")
elif temp_f < COLD_THRESHOLD:
    send_discord_alert(f"❄️ Cold alert! {temp_f}°F — below your {COLD_THRESHOLD}°F threshold.")

log_df = pd.DataFrame({
    "date": [str(today)],
    "time": [current_time],
    "temperature_2m": [current_temp],
    "temp_f": [round( temp_c* 9/5 + 32, 1)]
})

import plotly.graph_objects as go

def generate_dashboard():
    df = pd.read_csv("daily_log.csv", skipinitialspace=True)
    df["datetime"] = pd.to_datetime(df["time"])
    df = df.sort_values("datetime")

    max_idx = df["temp_f"].idxmax()
    min_idx = df["temp_f"].idxmin()

    fig = go.Figure()

    fig.add_scatter(x=df["datetime"], y=df["temp_f"],
                    mode="lines+markers", name="Temp (°F)",
                    line=dict(color="steelblue", width=2),
                    marker=dict(size=5))

    fig.add_scatter(x=[df.loc[max_idx, "datetime"]], y=[df.loc[max_idx, "temp_f"]],
                    mode="markers+text",
                    marker=dict(color="red", size=12),
                    text=[f"Max: {df.loc[max_idx, 'temp_f']}°F"],
                    textposition="top right",
                    name="Max")

    fig.add_scatter(x=[df.loc[min_idx, "datetime"]], y=[df.loc[min_idx, "temp_f"]],
                    mode="markers+text",
                    marker=dict(color="blue", size=12),
                    text=[f"Min: {df.loc[min_idx, 'temp_f']}°F"],
                    textposition="bottom right",
                    name="Min")

    fig.update_layout(
        title="My City Temperature Dashboard",
        yaxis_title="Temperature (°F)",
        xaxis_title="Date / Time"
    )

    fig.write_html("dashboard.html", include_plotlyjs='cdn')
    
def send_discord_alert(message):
    if not DISCORD_WEBHOOK_URL:
        print("No Discord webhook configured.")
        return
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    if response.status_code == 204:
        print("Discord alert sent.")
    else:
        print(f"Discord alert failed: {response.status_code}")
        
#print(df[["datetime", "temp_f"]])
print(df.dtypes)
print(df.columns)

generate_dashboard()

log_file = "daily_log.csv"
log_df.to_csv(log_file, mode='a', header=not os.path.isfile(log_file), index=False)
print(f"Logged current temperature: {current_temp}°C at {current_time}")


