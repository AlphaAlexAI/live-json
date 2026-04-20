#!/usr/bin/env python3
"""
Fetch follower counts from Instagram web profile info API.

Set USERS (comma-separated Instagram usernames).

One account: prints a single integer. Two or more: prints n1+n2+...= total.

On full success, prints JSON data and writes the same to data/instagram.json.
If any request fails, the JSON file is not modified.
"""

from __future__ import annotations

import json
import os
import random
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

INSTAGRAM_JSON_PATH = Path(__file__).resolve().parent.parent / "data" / "instagram.json"
_IG_APP_ID = "936619743392459"
_FINGERPRINTS = [
    "chrome124",
    "chrome123",
    "chrome120",
    "edge120",
    "safari17",
]


def info(message: str) -> None:
    print(f"[info] {message}", flush=True)


def parse_users_from_env() -> list[str]:
    raw = os.environ.get("USERS", "").strip()
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(",")]
    return [p for p in parts if p]


def fetch_follower_count(username: str) -> int:
    q = urllib.parse.quote(username, safe="")
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={q}"
    headers = {
        "x-ig-app-id": _IG_APP_ID,
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://www.instagram.com/",
    }
    for fp in _FINGERPRINTS:
        info(f"request web_profile_info (username={username}, fp={fp})")
        try:
            resp = requests.get(url, headers=headers, impersonate=fp, timeout=20)
            if resp.status_code != 200:
                info(f"response HTTP {resp.status_code} (retrying)")
                time.sleep(random.uniform(2, 5))
                continue
            payload = resp.json()
            n = int(payload["data"]["user"]["edge_followed_by"]["count"])
            info(f"parsed follower_count={n}")
            return n
        except Exception as e:
            info(f"request failed ({e})")
            time.sleep(random.uniform(2, 5))
    raise SystemExit(
        f"Unable to fetch follower count for {username} after trying all fingerprints"
    )


def instagram_username_field(names: list[str]) -> str:
    def one(n: str) -> str:
        n = n.strip()
        return n if n.startswith("@") else f"@{n}"

    if len(names) == 1:
        return one(names[0])
    return " + ".join(one(n) for n in names)


def main() -> None:
    info("loading configuration")
    names = parse_users_from_env()
    if not names:
        raise SystemExit(
            "Set USERS in the environment to a comma-separated list of Instagram usernames."
        )

    n_accounts = len(names)
    info(f"fetching followers for {n_accounts} account(s)")

    counts: list[int] = []
    for u in names:
        counts.append(fetch_follower_count(u))

    if len(counts) == 1:
        summary = str(counts[0])
        followers = counts[0]
    else:
        total = sum(counts)
        summary = "+".join(str(c) for c in counts) + f"= {total}"
        followers = total

    info(f"summary {summary}")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {
        "instagram": {
            "username": instagram_username_field(names),
            "followers": followers,
            "last_updated": now,
        }
    }
    text = json.dumps(data, indent=2) + "\n"

    rel_json = INSTAGRAM_JSON_PATH.relative_to(INSTAGRAM_JSON_PATH.parent.parent)
    info(f"writing {rel_json.as_posix()}")
    INSTAGRAM_JSON_PATH.write_text(text, encoding="utf-8")
    print(text, end="")
    info("done")


if __name__ == "__main__":
    main()
