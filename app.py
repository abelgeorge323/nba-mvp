# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from data_model import predict_breakouts

st.set_page_config(page_title="NBA Breakout & Value MVP", layout="wide")
st.title("🏀 NBA Breakout & Value MVP")

if not os.path.isfile("model.pkl"):
    st.error("Model not found. Run 'python data_model.py' first.")
    st.stop()

model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')

breakouts = predict_breakouts(model, scaler, season='2023-24')

# Top 10 breakout table
st.header("🔥 Top 10 Breakout Candidates (PTS jump prediction)")
top10 = breakouts.sort_values('breakout_prob', ascending=False).head(10)[['PLAYER_NAME', 'breakout_prob']]
st.dataframe(top10)

# Value score (simple composite)
breakouts['ValueScore'] = (
    0.4 * breakouts['PTS'] +
    0.3 * breakouts['REB'] +
    0.2 * breakouts['AST'] +
    0.1 * breakouts['STL']
)

# Scatter plot
st.header("💰 Value vs Scoring")
fig = px.scatter(
    breakouts.head(50),
    x='PTS',
    y='ValueScore',
    size='GP',
    color='breakout_prob',
    hover_data=['PLAYER_NAME'],
    title="Top 50 Players – Bubble size = Games Played"
)
st.plotly_chart(fig, use_container_width=True)

# Download button
csv = breakouts.to_csv(index=False)
st.download_button("📥 Download full CSV", csv, "breakouts.csv", "text/csv")