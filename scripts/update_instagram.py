#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime, timezone
from pathlib import Path

USERNAME = "haxorlex"
OUTPUT_FILE = Path("data/instagram.json")

def fetch_instagram_followers(username):
    """Fetch public follower count using i.instagram.com API"""
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "x-ig-app-id": "936619743392459",
    }
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        return data.get("data", {}).get("user", {}).get("edge_followed_by", {}).get("count", 0)
    else:
        print(f"[!] Failed to fetch data: HTTP {r.status_code}")
        return None

def save_json(username, followers):
    """Write the JSON file in desired format"""
    payload = {
        "instagram": {
            "username": f"@{username}",
            "followers": followers,
            "last_updated": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"✅ Saved {OUTPUT_FILE} with {followers} followers")

def main():
    followers = fetch_instagram_followers(USERNAME)
    if followers is not None:
        save_json(USERNAME, followers)
    else:
        print("⚠️ No data saved (fetch failed).")

if __name__ == "__main__":
    main()

