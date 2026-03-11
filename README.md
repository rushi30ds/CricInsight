# 🏏 CricPulse — IPL Analytics Dashboard

CricPulse is a full-stack cricket analytics web application that combines
**historical IPL data analysis** with **live match data** from CricAPI.

---

## 📁 Project Structure

```
CricPulse/
│
├── backend/
│   ├── app.py              # Flask app — all API routes
│   ├── match_stats.py      # Teams list + head-to-head stats (CSV)
│   ├── player_stats.py     # Team records, batting & bowling stats (CSV)
│   ├── ipl_matches.csv     # Historical IPL match data
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   └── index.html          # Full dashboard (HTML + CSS + JS)
│
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Install dependencies
```bash
cd CricPulse/backend
pip install -r requirements.txt
```

### 2. Run the Flask server
```bash
python app.py
```
Server starts at `http://127.0.0.1:5000`

### 3. Open the frontend
Open `frontend/index.html` directly in your browser.

---

## 🔌 API Endpoints

### Historical (CSV-based)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/teams` | All IPL teams |
| GET | `/api/teamvteam?team1=X&team2=Y` | Head-to-head stats |
| GET | `/api/team-record?team=X` | Full team record vs all opponents |
| GET | `/api/batting-record?batsman=X` | Career batting stats |
| GET | `/api/bowling-record?bowler=X` | Career bowling stats |

### Live (CricAPI)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/live-scores` | Current live match scores |
| GET | `/api/ipl-schedule` | IPL series & fixtures |
| GET | `/api/series-matches?id=X` | Matches for a series |
| GET | `/api/player-search?name=X` | Search players by name |
| GET | `/api/player-info?id=X` | Full player profile + photo |
| GET | `/api/match-scorecard?id=X` | Full match scorecard |

---

## 🛠️ Technologies Used

- **Backend** — Python, Flask, Flask-CORS, Pandas, NumPy
- **Live Data** — CricAPI (cricketdata.org)
- **Frontend** — HTML5, CSS3, Vanilla JavaScript
- **Data** — IPL historical CSV + CricAPI live feeds

---

## ✨ Features

- 🔴 Live Scores with auto-refresh
- 📅 IPL Schedule & fixtures
- 🔍 Player Search with photo, bio & career stats
- 🏟️ All IPL Teams browser
- ⚔️ Head-to-Head visual comparison
- 📊 Full Team Record vs every opponent
- 🏏 Batsman Stats — runs, avg, SR, 50s, 100s
- ⚡ Bowler Stats — wickets, economy, best figures
