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
    "chrome136",
    "chrome131",
    "chrome124",
    "chrome123",
    "chrome120",
    "chrome119",
    "chrome116",
    "chrome110",
    "chrome107",
    "chrome104",
    "chrome101",
    "chrome100",
    "chrome99",
    "edge101",
    "edge99",
    "safari15_5",
    "safari15_3",
    "safari18_0",
]
_MAX_ATTEMPTS_PER_FINGERPRINT = 2
_MAX_FINGERPRINT_ROUNDS = 3
_UNSUPPORTED_FINGERPRINTS: set[str] = set()


def info(message: str) -> None:
    print(f"[info] {message}", flush=True)


def parse_users_from_env() -> list[str]:
    raw = os.environ.get("USERS", "").strip()
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(",")]
    return [p for p in parts if p]


def _is_unsupported_impersonation_error(err: Exception) -> bool:
    return "is not supported" in str(err).lower()


def fetch_follower_count(username: str) -> int:
    q = urllib.parse.quote(username, safe="")
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={q}"
    headers = {
        "x-ig-app-id": _IG_APP_ID,
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://www.instagram.com/",
    }
    for round_idx in range(1, _MAX_FINGERPRINT_ROUNDS + 1):
        fps = [fp for fp in _FINGERPRINTS if fp not in _UNSUPPORTED_FINGERPRINTS]
        if not fps:
            raise SystemExit(
                "No supported fingerprints left. "
                "Update _FINGERPRINTS to versions supported by current curl_cffi build."
            )
        random.shuffle(fps)
        info(f"fingerprint round {round_idx}/{_MAX_FINGERPRINT_ROUNDS}")
        for fp in fps:
            for attempt in range(1, _MAX_ATTEMPTS_PER_FINGERPRINT + 1):
                info(
                    "request web_profile_info "
                    f"(username={username}, fp={fp}, attempt={attempt}/{_MAX_ATTEMPTS_PER_FINGERPRINT})"
                )
                try:
                    resp = requests.get(url, headers=headers, impersonate=fp, timeout=20)
                    if resp.status_code != 200:
                        info(f"response HTTP {resp.status_code} (rotating/retrying)")
                        time.sleep(random.uniform(2, 5))
                        continue
                    payload = resp.json()
                    n = int(payload["data"]["user"]["edge_followed_by"]["count"])
                    info(f"parsed follower_count={n}")
                    return n
                except Exception as e:
                    if _is_unsupported_impersonation_error(e):
                        info(f"fingerprint unsupported by current curl_cffi build (fp={fp}), skipping")
                        _UNSUPPORTED_FINGERPRINTS.add(fp)
                        break
                    info(f"request failed ({e})")
                    time.sleep(random.uniform(2, 5))
    raise SystemExit(
        "Unable to fetch follower count for "
        f"{username} after {_MAX_FINGERPRINT_ROUNDS} rounds "
        f"x {len(_FINGERPRINTS)} fingerprints "
        f"x {_MAX_ATTEMPTS_PER_FINGERPRINT} attempts"
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
