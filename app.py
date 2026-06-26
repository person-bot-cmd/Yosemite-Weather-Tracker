import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("My City Temperature Dashboard")

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
                mode="markers+text", marker=dict(color="red", size=12),
                text=[f"Max: {df.loc[max_idx, 'temp_f']}°F"],
                textposition="top right", name="Max")

fig.add_scatter(x=[df.loc[min_idx, "datetime"]], y=[df.loc[min_idx, "temp_f"]],
                mode="markers+text", marker=dict(color="blue", size=12),
                text=[f"Min: {df.loc[min_idx, 'temp_f']}°F"],
                textposition="bottom right", name="Min")

fig.update_layout(yaxis_title="Temperature (°F)", xaxis_title="Date / Time")

st.plotly_chart(fig, use_container_width=True)
