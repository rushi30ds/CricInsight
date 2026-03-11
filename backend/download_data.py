"""
download_data.py  —  CricPulse
Run this ONCE to download the ball-by-ball data locally.
After this, app.py will load instantly every time.

Usage:
    python download_data.py
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = os.path.join(BASE_DIR, "ipl_balls.csv")

URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"

print("⏳ Downloading ball-by-ball data from Google Sheets...")
print("   This may take 30–60 seconds depending on your connection...\n")

try:
    df = pd.read_csv(URL)
    df.to_csv(OUTPUT, index=False)
    print(f"✅ Done! Saved {len(df):,} rows to ipl_balls.csv")
    print(f"   Location: {OUTPUT}")
    print("\n🚀 You can now run: python app.py")
except Exception as e:
    print(f"❌ Failed to download: {e}")
    print("   Check your internet connection and try again.")
