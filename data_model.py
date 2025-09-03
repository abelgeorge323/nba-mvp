# data_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

def fetch_season_stats(season='2023-24'):
    """
    Returns the 2023-24 player box-score stats.
    On Streamlit Cloud we rely on the pre-saved CSV;
    on local machines we fall back to the NBA-API if the CSV is missing.
    """
    csv_path = 'data_2023_24.csv'
    if os.path.isfile(csv_path):
        return pd.read_csv(csv_path)

    # local fallback
    from nba_api.stats.endpoints import leaguedashplayerstats
    data = leaguedashplayerstats.LeagueDashPlayerStats(season=season).get_data_frames()[0]
    cols = ['PLAYER_NAME', 'AGE', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK',
            'TOV', 'FG_PCT', 'FG3_PCT', 'FT_PCT']
    return data[cols]

def build_training_data():
    frames = []
    for year in ['2021-22', '2022-23', '2023-24']:
        df = fetch_season_stats(year)
        df['SEASON'] = year
        frames.append(df)
    data = pd.concat(frames)

    # sort and create breakout label
    data = data.sort_values(['PLAYER_NAME', 'SEASON'])
    data['PTS_prev'] = data.groupby('PLAYER_NAME')['PTS'].shift(1)
    data['breakout'] = ((data['PTS'] - data['PTS_prev'] > 5) &
                        (data['GP'] >= 50)).astype(int)

    features = ['AGE', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV',
                'FG_PCT', 'FG3_PCT', 'FT_PCT', 'PTS_prev']
    df = data.dropna(subset=features + ['breakout'])
    X = df[features]
    y = df['breakout']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X_scaled, y)

    joblib.dump(model, 'model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    print("Model & scaler saved.")
    return model, scaler

def predict_breakouts(model, scaler, season='2023-24'):
    df = fetch_season_stats(season)
    # create dummy PTS_prev for scoring
    df['PTS_prev'] = df['PTS'] * 0.9
    features = ['AGE', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV',
                'FG_PCT', 'FG3_PCT', 'FT_PCT', 'PTS_prev']
    df = df[features].fillna(0)
    X_scaled = scaler.transform(df)
    df['breakout_prob'] = model.predict_proba(X_scaled)[:, 1]
    df['PLAYER_NAME'] = fetch_season_stats(season)['PLAYER_NAME']
    return df[['PLAYER_NAME', 'breakout_prob', 'AGE', 'GP', 'MIN', 'PTS',
               'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG_PCT', 'FG3_PCT', 'FT_PCT']]

if __name__ == "__main__":
    build_training_data()
