import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from data_model import predict_breakouts

st.set_page_config(page_title="NBA 2024-25 Breakout & Value MVP", layout="wide")
st.title("🏀 NBA 2024-25 Breakout & Value MVP")

# ---- SIDEBAR CONTROLS ----
year = st.sidebar.selectbox("Season", ["2023-24", "2024-25"], index=1)

metrics = {
    "Breakout Probability": "breakout_prob",
    "Points per Game": "PTS",
    "Value Score": "ValueScore",
    "Games Played": "GP",
}
metric_pretty = st.sidebar.selectbox("Color / Y-axis metric", list(metrics.keys()))
metric_col = metrics[metric_pretty]

# ---- LOAD DATA ----
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')
df = predict_breakouts(model, scaler, season=year)

# helper columns
df['ValueScore'] = 0.4 * df['PTS'] + 0.3 * df['REB'] + 0.2 * df['AST'] + 0.1 * df['STL']
df['USG_PCT'] = 25.0  # placeholder if not in data

# ---- UI ----
top10 = df.sort_values(metric_col, ascending=False).head(10)[['PLAYER_NAME', metric_col]]
st.header(f"🔥 Top 10 – {metric_pretty}")
st.dataframe(top10, use_container_width=True)

# use top 50 by the selected metric (not just the first 50 rows)
plot_df = df.sort_values(metric_col, ascending=False).head(50)

fig = px.scatter(
    plot_df,
    x='PTS',
    y=metric_col,
    size='GP',
    color=metric_col,
    hover_data=['PLAYER_NAME'],
    title=f"Top 50 Players – {metric_pretty} vs Scoring"
)

# only lock the y-axis for Value Score
if metric_col == "ValueScore":
    fig.update_yaxes(range=[0, 20])

st.plotly_chart(fig, use_container_width=True)

# ---- DOWNLOAD ----
csv = df.to_csv(index=False)
st.download_button(f"📥 Download CSV ({year})", csv, f"nba_{year}.csv")
