#!/usr/bin/env python3
"""
X (Twitter) API v2 — Research helper for podcast production.

Usage:
  python3 scripts/x_search.py "AI news" --max 20 --hours 24
  python3 scripts/x_search.py "LLM release" --max 10 --hours 48 --out research.json

Requires: X_BEARER_TOKEN in environment or .env file.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path


def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())


def search_x(query: str, max_results: int = 20, hours_back: int = 48) -> list[dict]:
    token = os.environ.get("X_BEARER_TOKEN", "")
    if not token or token == "your_bearer_token_here":
        print("ERROR: X_BEARER_TOKEN not set in .env", file=sys.stderr)
        sys.exit(1)

    start_time = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    # Exclude retweets and replies for cleaner signal
    full_query = f"({query}) lang:en -is:retweet -is:reply has:links"

    params = urllib.parse.urlencode(
        {
            "query": full_query,
            "max_results": min(max(10, max_results), 100),
            "start_time": start_time,
            "tweet.fields": "created_at,public_metrics,author_id,entities",
            "expansions": "author_id",
            "user.fields": "name,username,verified,public_metrics",
            "sort_order": "relevancy",
        }
    )

    url = f"https://api.twitter.com/2/tweets/search/recent?{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR: X API {e.code} — {body}", file=sys.stderr)
        sys.exit(1)

    users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
    results = []

    for tweet in data.get("data", []):
        author = users.get(tweet.get("author_id"), {})
        metrics = tweet.get("public_metrics", {})
        urls = [
            u.get("expanded_url", "")
            for u in tweet.get("entities", {}).get("urls", [])
            if not u.get("expanded_url", "").startswith("https://t.co")
        ]

        results.append(
            {
                "tweet_id": tweet["id"],
                "text": tweet["text"],
                "author": author.get("name", ""),
                "username": author.get("username", ""),
                "author_followers": author.get("public_metrics", {}).get(
                    "followers_count", 0
                ),
                "created_at": tweet.get("created_at", ""),
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "engagement": metrics.get("like_count", 0)
                + metrics.get("retweet_count", 0) * 3,
                "urls": urls,
            }
        )

    # Sort by engagement signal
    results.sort(key=lambda t: t["engagement"], reverse=True)
    return results


def main():
    load_env()

    parser = argparse.ArgumentParser(description="Search X (Twitter) for podcast research")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max", type=int, default=20, help="Max results (10-100)")
    parser.add_argument("--hours", type=int, default=48, help="Hours back to search")
    parser.add_argument("--out", help="Write JSON output to this file path")
    args = parser.parse_args()

    results = search_x(args.query, args.max, args.hours)

    output = {
        "query": args.query,
        "hours_back": args.hours,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "tweets": results,
    }

    json_out = json.dumps(output, indent=2, ensure_ascii=False)

    if args.out:
        Path(args.out).write_text(json_out)
        print(f"Saved {len(results)} tweets to {args.out}")
    else:
        print(json_out)


if __name__ == "__main__":
    main()
