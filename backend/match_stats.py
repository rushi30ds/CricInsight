"""
match_stats.py  —  CricPulse
Handles team listings and head-to-head statistics from local CSV data.
"""

import numpy as np
import pandas as pd
import os

# ── DATA LOADING ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
matches = pd.read_csv(os.path.join(BASE_DIR, "ipl_matches.csv"))


# ── API FUNCTIONS ──

def teamsAPI():
    """Returns a sorted list of all IPL teams."""
    teams = sorted(list(set(list(matches['Team1']) + list(matches['Team2']))))
    return {'teams': teams}


def teamVteamAPI(team1, team2):
    """Returns head-to-head stats between two teams."""
    valid_teams = list(set(list(matches['Team1']) + list(matches['Team2'])))

    if team1 not in valid_teams or team2 not in valid_teams:
        return {'message': 'Invalid team name. Please check the team name and try again.'}

    team_df = matches[
        ((matches['Team1'] == team1) & (matches['Team2'] == team2)) |
        ((matches['Team1'] == team2) & (matches['Team2'] == team1))
    ]

    total_matches = int(team_df.shape[0])

    wins_team1 = int(team_df['WinningTeam'].value_counts().get(team1, 0))
    wins_team2 = int(team_df['WinningTeam'].value_counts().get(team2, 0))
    draws = total_matches - (wins_team1 + wins_team2)

    return {
        'total_matches': total_matches,
        team1: wins_team1,
        team2: wins_team2,
        'draws': int(draws)
    }
