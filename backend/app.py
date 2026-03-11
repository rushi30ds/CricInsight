"""
app.py  —  CricPulse
Main Flask application. Exposes REST API for both
CSV-based historical analytics and live CricAPI data.
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests
import os

import match_stats
import player_stats

app = Flask(__name__)
CORS(app,origins=["https://cric-in-sight.netlify.app"])

CRICAPI_KEY  = "cb21ebff-f95b-44fb-8a0e-96dc045065c0"
CRICAPI_BASE = "https://api.cricapi.com/v1"


# ════════════════════════════════════════════
#  HISTORICAL CSV ROUTES  (match_stats / player_stats)
# ════════════════════════════════════════════

@app.route('/')
def home():
    return "CricPulse API is Online 🏏"


@app.route('/api/teams')
def teams():
    """List of all IPL teams from historical data."""
    return jsonify(match_stats.teamsAPI())


@app.route('/api/teamvteam')
def teamvteam():
    """Head-to-head stats between two teams."""
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    if not team1 or not team2:
        return jsonify({'error': 'team1 and team2 parameters are required'}), 400
    return jsonify(match_stats.teamVteamAPI(team1, team2))


@app.route('/api/team-record')
def team_record():
    """Full win/loss record for a team overall and vs each opponent."""
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({'error': 'team parameter is required'}), 400
    response = player_stats.teamAPI(team_name)
    return Response(response, mimetype='application/json')


@app.route('/api/batting-record')
def batting_record():
    """Career batting stats for a batsman."""
    batsman_name = request.args.get('batsman')
    if not batsman_name:
        return jsonify({'error': 'batsman parameter is required'}), 400
    response = player_stats.batsmanAPI(batsman_name)
    return Response(response, mimetype='application/json')


@app.route('/api/bowling-record')
def bowling_record():
    """Career bowling stats for a bowler."""
    bowler_name = request.args.get('bowler')
    if not bowler_name:
        return jsonify({'error': 'bowler parameter is required'}), 400
    response = player_stats.bowlerAPI(bowler_name)
    return Response(response, mimetype='application/json')


# ════════════════════════════════════════════
#  LIVE ROUTES  (CricAPI)
# ════════════════════════════════════════════


@app.route('/api/ipl-schedule')
def ipl_schedule():
    """IPL series list filtered from all active series."""
    try:
        res = requests.get(
            f"{CRICAPI_BASE}/series",
            params={"apikey": CRICAPI_KEY, "offset": 0},
            timeout=10
        )
        data = res.json()
        if data.get("status") == "success":
            all_series  = data.get("data", [])
            ipl_series  = [
                s for s in all_series
                if "IPL" in s.get("name", "").upper() or
                   "Indian Premier" in s.get("name", "")
            ]
            data["data"] = ipl_series if ipl_series else all_series[:20]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/series-matches')
def series_matches():
    """Fixture list for a given series id."""
    series_id = request.args.get('id')
    if not series_id:
        return jsonify({'error': 'id parameter is required'}), 400
    try:
        res = requests.get(
            f"{CRICAPI_BASE}/series_info",
            params={"apikey": CRICAPI_KEY, "id": series_id},
            timeout=10
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/player-search')
def player_search():
    """Search for a player by name."""
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'name parameter is required'}), 400
    try:
        res = requests.get(
            f"{CRICAPI_BASE}/players",
            params={"apikey": CRICAPI_KEY, "offset": 0, "search": name},
            timeout=10
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/player-info')
def player_info():
    """Full player profile including photo and career stats."""
    player_id = request.args.get('id')
    if not player_id:
        return jsonify({'error': 'id parameter is required'}), 400
    try:
        res = requests.get(
            f"{CRICAPI_BASE}/players_info",
            params={"apikey": CRICAPI_KEY, "id": player_id},
            timeout=10
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/match-scorecard')
def match_scorecard():
    """Full batting and bowling scorecard for a match."""
    match_id = request.args.get('id')
    if not match_id:
        return jsonify({'error': 'id parameter is required'}), 400
    try:
        res = requests.get(
            f"{CRICAPI_BASE}/match_scorecard",
            params={"apikey": CRICAPI_KEY, "id": match_id},
            timeout=10
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
