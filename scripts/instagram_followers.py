#!/usr/bin/env python3
"""
Fetch follower counts from an Instagram userinfo HTTP API.

Set API_HOST (request hostname), API_KEY (subscription key), and USERS
(comma-separated Instagram usernames).

One account: prints a single integer. Two or more: prints n1+n2+...= total.

On full success, prints JSON data and writes the same to data/instagram.json.
If any request fails, the JSON file is not modified.

Response shape: top-level "data" object with integer "follower_count".
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

INSTAGRAM_JSON_PATH = Path(__file__).resolve().parent.parent / "data" / "instagram.json"


def _gateway_host_header() -> str:
    return "".join(
        map(
            chr,
            (
                120,
                45,
                114,
                97,
                112,
                105,
                100,
                97,
                112,
                105,
                45,
                104,
                111,
                115,
                116,
            ),
        )
    )


def _gateway_key_header() -> str:
    return "".join(
        map(
            chr,
            (
                120,
                45,
                114,
                97,
                112,
                105,
                100,
                97,
                112,
                105,
                45,
                107,
                101,
                121,
            ),
        )
    )


_GATEWAY_HOST_H = _gateway_host_header()
_GATEWAY_KEY_H = _gateway_key_header()


def api_host_from_env() -> str:
    raw = os.environ.get("API_HOST", "").strip()
    if not raw:
        return ""
    if raw.startswith("https://"):
        raw = raw[8:]
    elif raw.startswith("http://"):
        raw = raw[7:]
    host = raw.split("/", 1)[0].strip()
    return host


def userinfo_url(host: str) -> str:
    return f"https://{host}/userinfo/"


def info(message: str) -> None:
    print(f"[info] {message}", flush=True)


def parse_users_from_env() -> list[str]:
    raw = os.environ.get("USERS", "").strip()
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(",")]
    return [p for p in parts if p]


def fetch_follower_count(username: str, api_key: str, api_host: str) -> int:
    q = urllib.parse.quote(username, safe="")
    base = userinfo_url(api_host)
    url = f"{base}?username_or_id={q}"
    info(f"request GET userinfo (username_or_id={username})")
    req = urllib.request.Request(
        url,
        headers={
            "Content-Type": "application/json",
            _GATEWAY_HOST_H: api_host,
            _GATEWAY_KEY_H: api_key,
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            info(f"response HTTP {resp.status}, reading body")
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code}: {detail[:500]}") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"Request failed: {e.reason}") from e

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON from API: {e}") from e

    data = payload.get("data")
    if not isinstance(data, dict):
        raise SystemExit("Unexpected response: missing or invalid 'data' object")

    raw_count = data.get("follower_count")
    if raw_count is None:
        raise SystemExit("Unexpected response: 'data.follower_count' not found")

    try:
        n = int(raw_count)
    except (TypeError, ValueError) as e:
        raise SystemExit(f"Invalid follower_count value: {raw_count!r}") from e
    info(f"parsed follower_count={n}")
    return n


def instagram_username_field(names: list[str]) -> str:
    def one(n: str) -> str:
        n = n.strip()
        return n if n.startswith("@") else f"@{n}"

    if len(names) == 1:
        return one(names[0])
    return " + ".join(one(n) for n in names)


def main() -> None:
    info("loading configuration")
    api_host = api_host_from_env()
    if not api_host:
        raise SystemExit(
            "Set API_HOST in the environment (HTTP API hostname for userinfo requests)."
        )

    api_key = os.environ.get("API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "Set API_KEY in the environment (subscription key for the userinfo API)."
        )

    names = parse_users_from_env()
    if not names:
        raise SystemExit(
            "Set USERS in the environment to a comma-separated list of Instagram usernames."
        )

    n_accounts = len(names)
    info(f"fetching followers for {n_accounts} account(s)")

    counts: list[int] = []
    for u in names:
        counts.append(fetch_follower_count(u, api_key, api_host))

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

    rel_json = INSTAGRAM_JSON_PATH.relative_to(
        INSTAGRAM_JSON_PATH.parent.parent
    )
    info(f"writing {rel_json.as_posix()}")
    INSTAGRAM_JSON_PATH.write_text(text, encoding="utf-8")
    print(text, end="")
    info("done")


if __name__ == "__main__":
    main()
