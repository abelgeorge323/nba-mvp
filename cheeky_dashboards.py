# cheeky_dashboards.py
import streamlit as st, pandas as pd, numpy as np, requests, os, feedparser, glob
import google.generativeai as genai

GEMINI_KEY = "AIzaSyBpzFnrOZYXeTa1H3QNxj3Ym0v5McvzcIk"  # <- tomorrow move to .env

# ---------- 1.  auto-detect & merge the 5 CSVs ----------
@st.cache_data(ttl=600)
def load_mega_frame():
    csvs = glob.glob("NBA_2025_*.csv")
    mega = None
    for f in csvs:
        df = pd.read_csv(f)
        # standardise player name
        for col in ["Player", "PLAYER_NAME", "PLAYER"]:
            if col in df.columns:
                df = df.rename(columns={col: "Player"})
                break
        # bring in every other column
        cols = [c for c in df.columns if c != "Player"]
        if mega is None:
            mega = df[["Player"]].copy()
        mega = mega.merge(df[cols], on="Player", how="outer", suffixes=("", f"_{f.split('.')[0]}"))
    return mega

# ---------- 2.  GEMINI one-liner helper ----------
def gemini_one_liner(prompt):
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI joke failed: {e}"

# ---------- 3.  10 categories × 10 cheeky cards ----------
def show_cheeky_dashboards():
    st.markdown("### 😜 Cheeky NBA 2024-25 Dashboards")
    df = load_mega_frame()

    # ---- CATEGORY 1: Mr/Ms Everything (10 cards) ----
    if {"PTS", "AST", "REB"}.issubset(df.columns):
        with st.expander("🏀 Mr/Ms Everything (10 cards)", expanded=True):
            z = df[["PTS", "AST", "REB"]].apply(lambda x: (x - x.mean()) / x.std())
            df["Everywhere"] = z.sum(axis=1)
            top10 = df.nlargest(10, "Everywhere")
            for i, (_, row) in enumerate(top10.iterrows(), 1):
                prompt = f"{row.Player} ranks {i} in combined z-score (PTS+AST+REB). Write one cheeky 20-word sentence."
                card = gemini_one_liner(prompt)
                st.info(f"{i}. {card}")

    # ---- CATEGORY 2: Corner-3 King (10 cards) ----
    if {"FG3_PCT", "3P"}.issubset(df.columns):
        with st.expander("🎯 Corner-3 King (10 cards)", expanded=True):
            top10 = df.nlargest(10, "FG3_PCT")
            for i, (_, row) in enumerate(top10.iterrows(), 1):
                prompt = f"{row.Player} shoots {row.FG3_PCT:.1%} from three. Write one cheeky 20-word sentence."
                card = gemini_one_liner(prompt)
                st.info(f"{i}. {card}")

    # ---- CATEGORY 3: Turnover Tourist (10 cards) ----
    if {"USG_PCT", "TOV"}.issubset(df.columns):
        with st.expander("✈️ Turnover Tourist (10 cards)", expanded=True):
            df["Tourist"] = df["USG_PCT"] * df["TOV"]
            top10 = df.nlargest(10, "Tourist")
            for i, (_, row) in enumerate(top10.iterrows(), 1):
                prompt = f"{row.Player} has {row.USG_PCT:.1f}% usage and {row.TOV:.1f} TOV. Write one cheeky 20-word roast."
                card = gemini_one_liner(prompt)
                st.info(f"{i}. {card}")

    # ---- CATEGORY 4: Air Traffic Controller (10 cards) ----
    if {"AST", "TOV"}.issubset(df.columns):
        with st.expander("🚦 Air Traffic Controller (10 cards)", expanded=True):
            df["AST_TOV"] = df["AST"] / df["TOV"].clip(lower=0.1)
            cops = df.query("AST > 5").nlargest(10, "AST_TOV")
            for i, (_, row) in enumerate(cops.iterrows(), 1):
                prompt = f"{row.Player} AST/TOV = {row.AST_TOV:.1f}. Write one cheeky 20-word traffic-cop sentence."
                card = gemini_one_liner(prompt)
                st.info(f"{i}. {card}")

    # ---- CATEGORY 5: Block Party MVP (10 cards) ----
    if {"BLK", "MP"}.issubset(df.columns):
        with st.expander("🧱 Block Party MVP (10 cards)", expanded=True):
            df["BLK_per_36"] = df["BLK"] * 36 / df["MP"].clip(lower=1)
            top10 = df.nlargest(10, "BLK_per_36")
            for i, (_, row) in enumerate(top10.iterrows(), 1):
                prompt = f"{row.Player} blocks {row.BLK_per_36:.1f} per 36 min. Write one cheeky 20-word wall sentence."
                card = gemini_one_liner(prompt)
                st.info(f"{i}. {card}")

    # ---- CATEGORY 6: Efficiency Enigma (10 cards) ----
    if {"PTS", "MP"}.issubset(df.columns):
        with st.expander("⚡ Efficiency Enigma (10 cards)", expanded=True):
            df["PTS_per_36"] = df["PTS"] * 36 / df["MP"].clip(lower=1)
            top10 = df.nlargest(10, "PTS_per_36")
            for i, (_, row) in enumerate(top10.iterrows(), 1):
                prompt = f"{row.Player} scores {row.PTS_per_36:.1f} per 36. Write one cheeky 20-word sentence."
                card = gemini_one_liner(prompt)
                st.info(f"{i}. {card}")

    # ---- CATEGORY 7: Ironman (10 cards) ----
    if {"MP"}.issubset(df.columns):
        with st.expander("🛠️ Ironman (10 cards)", expanded=True):
            top10 = df.nlargest(10, "MP")
            for i, (_, row) in enumerate(top10.iterrows(), 1):
                prompt = f"{row.Player} played {row.MP:.0f} minutes. Write one cheeky 20-word ironman sentence."
                card = gemini_one_liner(prompt)
                st.info(f"{i}. {card}")

    # ---- CATEGORY 8: Triple-Double King (10 cards) ----
    if {"Trp-Dbl"}.issubset(df.columns):
        with st.expander("📊 Triple-Double King (10 cards)", expanded=True):
            top10 = df.nlargest(10, "Trp-Dbl")
            for i, (_, row) in enumerate(top10.iterrows(), 1):
                prompt = f"{row.Player} has {row['Trp-Dbl']} triple-doubles. Write one cheeky 20-word spreadsheet sentence."
                card = gemini_one_liner(prompt)
                st.info(f"{i}. {card}")

    # ---- CATEGORY 9: Mid-Range Cheat (10 cards) ----
    if {"eFG%"}.issubset(df.columns):
        with st.expander("🎯 Mid-Range Cheat (10 cards)", expanded=True):
            top10 = df.nlargest(10, "eFG%")
            for i, (_, row) in enumerate(top10.iterrows(), 1):
                prompt = f"{row.Player} mid-range eFG% = {row['eFG%']:.1%}. Write one cheeky 20-word physics sentence."
                card = gemini_one_liner(prompt)
                st.info(f"{i}. {card}")

    # ---- CATEGORY 10: Stat Sheet Stuffer (10 cards) ----
    if {"PTS", "REB", "AST", "STL", "BLK"}.issubset(df.columns):
        with st.expander("📈 Stat Sheet Stuffer (10 cards)", expanded=True):
            df["STUFF"] = df["PTS"] + df["REB"] + df["AST"] + df["STL"] + df["BLK"]
            top10 = df.nlargest(10, "STUFF")
            for i, (_, row) in enumerate(top10.iterrows(), 1):
                prompt = f"{row.Player} stuffed {row.STUFF:.0f} total stats. Write one cheeky 20-word spreadsheet sentence."
                card = gemini_one_liner(prompt)
                st.info(f"{i}. {card}")

# ---------- 4.  auto-Jira ticket (optional) ----------
def create_insight_ticket(title, body):
    try:
        from jira import JIRA
        jira = JIRA(server="https://foodtrx.atlassian.net", basic_auth=("abelgeorge323@gmail.com", os.getenv("JIRA_TOKEN")))
        issue = jira.create_issue(
            project={"key": "PRAC"},
            summary=title,
            description=body,
            issuetype={"name": "Task"}
        )
        return issue.key
    except Exception as e:
        return f"Ticket failed: {e}"

# ---------- 5.  wire into main ----------
def show_cheeky_dashboards():
    st.markdown("### 😜 Cheeky NBA 2024-25 Dashboards")
    