"""
player_stats.py  —  CricPulse
Handles team records, batting statistics, and bowling statistics from CSV data.
"""

import pandas as pd
import numpy as np
import json
import os
import requests
import io

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return None if np.isnan(obj) else float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
matches  = pd.read_csv(os.path.join(BASE_DIR, "ipl_matches.csv"))

_batter_data = None
_bowler_data = None

def _bowler_run(x):
    return 0 if x['extra_type'] in ['penalty', 'legbyes', 'byes'] else x['total_run']

def _bowler_wicket(x):
    return x['isWicketDelivery'] if x['kind'] in [
        'caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket'
    ] else 0

def _load_ball_data():
    global _batter_data, _bowler_data
    if _batter_data is not None:
        return

    BALLS_CSV = os.path.join(BASE_DIR, "ipl_balls.csv")

    if os.path.exists(BALLS_CSV):
        print("Loading ball-by-ball data from local file...")
        balls = pd.read_csv(BALLS_CSV)
        print(f"Loaded {len(balls):,} ball records.")
    else:
        print("Downloading ball-by-ball data for first time... (30-60 sec)")
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"
        r = requests.get(url, timeout=120, headers={"User-Agent": "Mozilla/5.0"})
        balls = pd.read_csv(io.StringIO(r.text))
        balls.to_csv(BALLS_CSV, index=False)
        print(f"Saved {len(balls):,} rows to ipl_balls.csv")

    ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()
    ball_withmatch['BowlingTeam'] = ball_withmatch.Team1 + ball_withmatch.Team2
    ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(
        lambda x: x.iloc[0].replace(x.iloc[1], ''), axis=1
    )

    _batter_data = ball_withmatch[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]
    _bowler_data = _batter_data.copy()
    _bowler_data['bowler_run']     = _bowler_data.apply(_bowler_run, axis=1)
    _bowler_data['isBowlerWicket'] = _bowler_data.apply(_bowler_wicket, axis=1)
    print("Ball data ready!")

def _team_vs_team(team, team2):
    df   = matches[
        ((matches['Team1'] == team) & (matches['Team2'] == team2)) |
        ((matches['Team2'] == team) & (matches['Team1'] == team2))
    ].copy()
    mp   = df.shape[0]
    won  = df[df.WinningTeam == team].shape[0]
    nr   = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr
    return {'matchesplayed': mp, 'won': won, 'loss': loss, 'noResult': nr}

def _all_record(team):
    df     = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()
    mp     = df.shape[0]
    won    = df[df.WinningTeam == team].shape[0]
    nr     = df[df.WinningTeam.isnull()].shape[0]
    loss   = mp - won - nr
    titles = df[(df.MatchNumber == 'Final') & (df.WinningTeam == team)].shape[0]
    return {'matchesplayed': mp, 'won': won, 'loss': loss, 'noResult': nr, 'title': titles}

def teamAPI(team, matches=matches):
    self_record = _all_record(team)
    TEAMS       = matches.Team1.unique()
    against     = {team2: _team_vs_team(team, team2) for team2 in TEAMS}
    data        = {team: {'overall': self_record, 'against': against}}
    return json.dumps(data, cls=NpEncoder)

def _batsman_record(batsman, df):
    if df.empty:
        return {}
    out         = df[df.player_out == batsman].shape[0]
    df          = df[df['batter'] == batsman]
    inngs       = df.ID.unique().shape[0]
    runs        = df.batsman_run.sum()
    fours       = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes       = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
    avg         = runs / out if out else None
    nballs      = df[~(df.extra_type == 'wides')].shape[0]
    strike_rate = runs / nballs * 100 if nballs else None
    gb       = df.groupby('ID').sum()
    fifties  = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
    hundreds = gb[gb.batsman_run >= 100].shape[0]
    try:
        highest_score = int(gb.batsman_run.max())
    except Exception:
        highest_score = None
    not_out = inngs - out
    mom     = df[df.Player_of_Match == batsman].drop_duplicates('ID').shape[0]
    return {
        'innings': inngs, 'runs': runs, 'fours': fours, 'sixes': sixes,
        'avg': avg, 'strikeRate': strike_rate, 'fifties': fifties,
        'hundreds': hundreds, 'highestScore': highest_score,
        'notOut': not_out, 'mom': mom
    }

def _batsman_vs_team(batsman, team, df):
    return _batsman_record(batsman, df[df.BowlingTeam == team].copy())

def batsmanAPI(batsman):
    _load_ball_data()
    df          = _batter_data[_batter_data.innings.isin([1, 2])]
    self_record = _batsman_record(batsman, df)
    TEAMS       = matches.Team1.unique()
    against     = {team: _batsman_vs_team(batsman, team, df) for team in TEAMS}
    data        = {batsman: {'all': self_record, 'against': against}}
    return json.dumps(data, cls=NpEncoder)

def _bowler_record(bowler, df):
    df     = df[df['bowler'] == bowler]
    inngs  = df.ID.unique().shape[0]
    nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs   = df['bowler_run'].sum()
    eco    = runs / nballs * 6 if nballs else None
    wicket = df.isBowlerWicket.sum()
    avg    = runs / wicket if wicket else None
    sr     = nballs / wicket if wicket else None
    gb = df.groupby('ID').sum()
    w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]
    try:
        best = gb.sort_values(
            ['isBowlerWicket', 'bowler_run'], ascending=[False, True]
        ).head(1).iloc[0]
        best_figure = f"{int(best['isBowlerWicket'])}/{int(best['bowler_run'])}"
    except Exception:
        best_figure = None
    mom = df[df.Player_of_Match == bowler].drop_duplicates('ID').shape[0]
    return {
        'innings': inngs, 'wicket': wicket, 'economy': eco,
        'average': avg, 'strikeRate': sr,
        'fours': df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0],
        'sixes': df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0],
        'best_figure': best_figure, '3+W': w3, 'mom': mom
    }

def _bowler_vs_team(bowler, team, df):
    return _bowler_record(bowler, df[df.BattingTeam == team].copy())

def bowlerAPI(bowler):
    _load_ball_data()
    df          = _bowler_data[_bowler_data.innings.isin([1, 2])]
    self_record = _bowler_record(bowler, df)
    TEAMS       = matches.Team1.unique()
    against     = {team: _bowler_vs_team(bowler, team, df) for team in TEAMS}
    data        = {bowler: {'all': self_record, 'against': against}}
    return json.dumps(data, cls=NpEncoder)
