# make_2024_25.py
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats

df = leaguedashplayerstats.LeagueDashPlayerStats(season='2024-25').get_data_frames()[0]
cols = ['PLAYER_NAME','AGE','GP','MIN','PTS','REB','AST','STL','BLK',
        'TOV','FG_PCT','FG3_PCT','FT_PCT']
df[cols].to_csv('data_2024_25.csv', index=False)
print("✅ data_2024_25.csv created")