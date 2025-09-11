# breakout_ai.py  (live-data edition)
import streamlit as st
import pandas as pd
import google.generativeai as genai
import requests, os

GEMINI_KEY = "AIzaSyBpzFnrOZYXeTa1H3QNxj3Ym0v5McvzcIk"   # your key

# ---------- 1.  LIVE ESPN NBA player stats ----------
@st.cache_data(ttl=600)
def live_nba_player_stats():
    """Live NBA per-player stats via NBA.com public API (no key)."""
    url = "https://stats.nba.com/stats/leagueLeaders?ActiveFlag=Yes&LeagueID=00&PerMode=PerGame&Scope=S&Season=2024-25&SeasonType=Regular+Season&StatCategory=PTS"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()

    headers_row = data["resultSet"]["headers"]   # e.g. ['PLAYER', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'FG_PCT', 'FG3_PCT']
    rows        = data["resultSet"]["rowSet"]
    df          = pd.DataFrame(rows, columns=headers_row)

    # rename to our friendly names
    df = df.rename(columns={
        "PLAYER": "PLAYER_NAME",
        "REB":    "REB",
        "AST":    "AST",
        "FG_PCT": "FG_PCT",
        "FG3_PCT": "FG3_PCT"
    })

    # keep only what we need + add placeholder age
    df = df[["PLAYER_NAME", "GP", "MIN", "PTS", "REB", "AST", "FG_PCT", "FG3_PCT"]].head(50)
    df["AGE"] = 25
    return df
# ---------- 2.  live ESPN headlines (no auth) ----------
def live_nba_buzz():
    try:
        import feedparser
        r = requests.get("https://www.espn.com/espn/rss/nba/news", timeout=5)
        feed = feedparser.parse(r.text)
        return "\n".join(entry.title for entry in feed.entries[:5])
    except Exception:
        return "Headlines unavailable."

# ---------- 3.  Ask AI with LIVE data ----------
def show_breakout_search():
    st.markdown("### 🔍 Ask AI (live 2024-25 NBA data + headlines)")
    question = st.text_input("Your question:", placeholder="e.g. Who is most likely to breakout and why?")
    if st.button("Ask AI"):
        if not question.strip():
            st.warning("Please type a question.")
            return

        df_live = live_nba_player_stats()
        csv_live = df_live.head(10).to_string(index=False)
        buzz = live_nba_buzz()

        prompt = (
            "You are an NBA analyst.  Use the LIVE ESPN stats below plus the recent headlines "
            "and general basketball knowledge.  Answer concisely (< 120 words).\n\n"
            f"ESPN headlines:\n{buzz}\n\n"
            f"Live ESPN player stats (top 10 by PTS):\n{csv_live}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        with st.spinner("AI thinking (live data + headlines)..."):
            response = model.generate_content(prompt)
        st.success("AI insight")
        st.write(response.text)

        with st.expander("See live top-10 scorers"):
            st.dataframe(df_live.head(10))