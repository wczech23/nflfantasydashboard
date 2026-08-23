import nflreadpy as nfl
import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    # TODO: set a realistic User-Agent; some fantasy sites block default
    # python-requests agents. Consider rotating agents if scraping at scale.
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

REQUEST_TIMEOUT = 15


# gathering player_stats
player_stats = nfl.load_player_stats([2025,2024,2023,2022,2021]).to_pandas()


for item in player_stats.columns:
    print(item)

final_cols = [
    'player_id', 'player_name', 'position', 'season', 'week', 'team', 'opponent_team',
    'passing_yards', 'passing_tds', 'passing_interceptions', 'sack_fumbles_lost',
    'rushing_yards', 'rushing_tds', 'rushing_fumbles_lost', 'rushing_first_downs',
    'receptions', 'targets', 'receiving_yards', 'receiving_tds', 'receiving_fumbles_lost', 'receiving_first_downs',
    'target_share', 'special_teams_tds', 'fantasy_points', 'fantasy_points_ppr'
]

player_stats = player_stats[final_cols]