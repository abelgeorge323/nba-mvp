# data_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# ---------- 1. Load & aggregate game logs ----------
def load_and_aggregate_game_logs(path='database_24_25.csv'):
    df = pd.read_csv(path)
    df['Data'] = pd.to_datetime(df['Data'])

    # Per-player averages across all games
    agg = df.groupby('Player').agg(
        GP=('PTS', 'count'),
        MIN=('MP', 'mean'),
        PTS=('PTS', 'mean'),
        REB=('TRB', 'mean'),
        AST=('AST', 'mean'),
        STL=('STL', 'mean'),
        BLK=('BLK', 'mean'),
        TOV=('TOV', 'mean'),
        FG_PCT=('FG%', 'mean'),
        FG3_PCT=('3P%', 'mean'),
        FT_PCT=('FT%', 'mean'),
        RECENT_PTS=('PTS', lambda x: x.tail(5).mean())  # last-5-games avg
    ).reset_index()

    agg.rename(columns={'Player': 'PLAYER_NAME'}, inplace=True)
    agg['AGE'] = 25          # placeholder
    agg['PTS_prev'] = agg['PTS'] * 0.9  # synthetic prior
    return agg

# ---------- 2. Build training data (2024-25 only) ----------
def build_training_data():
    df = load_and_aggregate_game_logs()

    # Breakout = PTS jumps > 5 vs synthetic prior AND played ≥ 10 games
    df['breakout'] = ((df['RECENT_PTS'] - df['PTS_prev'] > 5) & (df['GP'] >= 10)).astype(int)

    features = ['AGE', 'GP', 'MIN', 'PTS_prev', 'REB', 'AST', 'STL', 'BLK', 'TOV',
                'FG_PCT', 'FG3_PCT', 'FT_PCT']
    df = df.dropna(subset=features + ['breakout'])

    X = df[features]
    y = df['breakout']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X_scaled, y)

    joblib.dump(model, 'model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    print("✅ 2024-25-only model trained & saved.")

# ---------- 3. Predict ----------
def predict_breakouts(model, scaler, season='2024-25'):
    df = load_and_aggregate_game_logs()
    df['PTS_prev'] = df['PTS'] * 0.9
    features = ['AGE', 'GP', 'MIN', 'PTS_prev', 'REB', 'AST', 'STL', 'BLK', 'TOV',
                'FG_PCT', 'FG3_PCT', 'FT_PCT']
    df = df[features].fillna(0)
    X_scaled = scaler.transform(df)
    df['breakout_prob'] = model.predict_proba(X_scaled)[:, 1]
    df['PLAYER_NAME'] = df['PLAYER_NAME']
    return df[['PLAYER_NAME', 'breakout_prob', 'AGE', 'GP', 'MIN', 'PTS',
               'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG_PCT', 'FG3_PCT', 'FT_PCT']]

if __name__ == "__main__":
    build_training_data()