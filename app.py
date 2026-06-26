import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
 
st.set_page_config(page_title="My City Temperature Dashboard", layout="wide")
st.title("My City Temperature Dashboard")
 
# ── Load current readings ─────────────────────────────────────────────────────
df = pd.read_csv("daily_log.csv", skipinitialspace=True)
df["datetime"] = pd.to_datetime(df["time"])
df = df.sort_values("datetime")
 
# ── Load historical data ──────────────────────────────────────────────────────
hist = pd.read_csv("historical_weather.csv", skipinitialspace=True)
 
# Handle column naming — Open-Meteo uses "time" for hourly historical data
date_col = "date" if "date" in hist.columns else "time"
hist["date"] = pd.to_datetime(hist[date_col])
hist["temp_f"] = hist["temperature_2m"] * 9 / 5 + 32
 
# If data is hourly, resample to daily average first
if hist["date"].dt.hour.nunique() > 1:
    hist = hist.set_index("date").resample("D")["temp_f"].mean().reset_index()
    hist.columns = ["date", "temp_f"]
 
# Group by day of year to build the historical normal band
hist["day_of_year"] = hist["date"].dt.dayofyear
band = hist.groupby("day_of_year")["temp_f"].agg(["mean", "std"]).reset_index()
band["upper"] = band["mean"] + band["std"]
band["lower"] = band["mean"] - band["std"]
 
# Map day-of-year numbers to real dates in the current year for the x-axis
current_year = datetime.date.today().year
band["plot_date"] = band["day_of_year"].apply(
    lambda d: datetime.date(current_year, 1, 1) + datetime.timedelta(days=int(d) - 1)
)
band = band.sort_values("plot_date")
 
# ── Metric boxes ─────────────────────────────────────────────────────────────
max_idx = df["temp_f"].idxmax()
min_idx = df["temp_f"].idxmin()
 
col1, col2, col3 = st.columns(3)
col1.metric("Latest Reading", f"{df['temp_f'].iloc[-1]}°F")
col2.metric("All-Time Max", f"{df.loc[max_idx, 'temp_f']}°F")
col3.metric("All-Time Min", f"{df.loc[min_idx, 'temp_f']}°F")
 
# ── Chart ─────────────────────────────────────────────────────────────────────
fig = go.Figure()
 
# Historical band — upper boundary (invisible, anchors the fill)
fig.add_scatter(
    x=band["plot_date"], y=band["upper"],
    mode="lines", line=dict(width=0),
    showlegend=False, name="upper_bound"
)
 
# Historical band — lower boundary with shaded fill
fig.add_scatter(
    x=band["plot_date"], y=band["lower"],
    mode="lines", fill="tonexty",
    fillcolor="rgba(173, 216, 230, 0.25)",
    line=dict(width=0),
    name="Historical Normal Range"
)
 
# Historical daily average (dashed reference line)
fig.add_scatter(
    x=band["plot_date"], y=band["mean"],
    mode="lines",
    line=dict(color="rgba(100, 149, 237, 0.6)", width=1, dash="dash"),
    name="Historical Average"
)
 
# Current readings — main line
fig.add_scatter(
    x=df["datetime"], y=df["temp_f"],
    mode="lines+markers", name="My Readings",
    line=dict(color="steelblue", width=2),
    marker=dict(size=6)
)
 
# Max marker
fig.add_scatter(
    x=[df.loc[max_idx, "datetime"]], y=[df.loc[max_idx, "temp_f"]],
    mode="markers+text",
    marker=dict(color="red", size=12, symbol="star"),
    text=[f"Max: {df.loc[max_idx, 'temp_f']}°F"],
    textposition="top right",
    name="Max"
)
 
# Min marker
fig.add_scatter(
    x=[df.loc[min_idx, "datetime"]], y=[df.loc[min_idx, "temp_f"]],
    mode="markers+text",
    marker=dict(color="royalblue", size=12, symbol="star"),
    text=[f"Min: {df.loc[min_idx, 'temp_f']}°F"],
    textposition="bottom right",
    name="Min"
)
 
fig.update_layout(
    yaxis_title="Temperature (°F)",
    xaxis_title="Date",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
 
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Shaded band: historical normal range (mean ± 1 standard deviation by day of year). "
    "Dashed line: historical daily average. Current readings shown in blue."
)
