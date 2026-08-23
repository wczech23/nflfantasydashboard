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

final_cols = [
    'player_id', 'player_name', 'position', 'season', 'week', 'team', 'opponent_team',
    'passing_yards', 'passing_tds', 'passing_interceptions', 'sack_fumbles_lost',
    'rushing_yards', 'rushing_tds', 'rushing_fumbles_lost', 'rushing_first_downs',
    'receptions', 'targets', 'receiving_yards', 'receiving_tds', 'receiving_fumbles_lost', 'receiving_first_downs',
    'target_share', 'special_teams_tds', 'fantasy_points', 'fantasy_points_ppr'
]

player_stats = player_stats[final_cols]

# creating offset fields
week_lookup = (
    player_stats[['season', 'week']]
    .drop_duplicates()
    .sort_values(['season', 'week'], ascending=[False, False])
    .reset_index(drop=True)
)

season_lookup = (
    player_stats[['season']]
    .drop_duplicates()
    .sort_values(['season'], ascending=[False])
    .reset_index(drop=True)
)


week_lookup['week_offset'] = week_lookup.index
season_lookup['season_offset'] = season_lookup.index
# Merge the offset back onto the main table
player_stats = player_stats.merge(week_lookup, on=['season', 'week'], how='left')
player_stats = player_stats.merge(season_lookup, on=['season'], how='left')


# gathering injuries, schedules, depth chart filtered to latest date for each player
inj = nfl.load_injuries().to_pandas()
sched = nfl.load_schedules([2026]).to_pandas()
depth = nfl.load_depth_charts([2026]).to_pandas()
depth_latest = (
    depth.sort_values('dt')
        .groupby(['player_name','espn_id','team'])
        .tail(1)
)

# gathering remaining sos for each team
response = requests.get("https://www.tankathon.com/nfl/remaining-schedule-strength", headers=HEADERS, timeout=REQUEST_TIMEOUT)
response.raise_for_status()
html = response.text
soup = BeautifulSoup(html,'html.parser')

table = soup.find(id='remaining-schedule-strength')
rows = []
for row in table.find_all('div', class_='flex-row'):
    cells = row.find_all('div', class_='flex-cell', recursive=False)
    sos = cells[1].get_text(strip=True)
    rank = cells[0].find('div', class_='rank').get_text(strip=True)
    team_abbr = cells[0].find('div', class_='sos-abbr').get_text(strip=True)
        
    rows.append({
        'team_abbr':team_abbr,
        'rank':int(rank),
        'sos':float(sos)
    })
sos = pd.DataFrame(rows)

# writing out tables to Excel files
inj.to_excel('player_injuries.xlsx', index=False)
sched.to_excel('player_schedules.xlsx', index=False)
depth_latest.to_excel('player_depth.xlsx', index=False)
sos.to_excel('team_sos.xlsx', index=False)
player_stats.to_excel('player_stats.xlsx', index=False)