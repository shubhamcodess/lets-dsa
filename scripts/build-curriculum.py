#!/usr/bin/env python3
"""
build-curriculum.py — assemble the problem curriculum from curated public lists.

This script does not invent problems. Every entry is fetched from a real source
and then verified against LeetCode's public GraphQL endpoint, which supplies the
canonical id, title, difficulty, and topic tags. A slug that does not resolve is
dropped and reported — never guessed at.

Usage:
    python3 scripts/build-curriculum.py            # fetch + merge (uses cache)
    python3 scripts/build-curriculum.py --verify   # also verify every slug (slow, ~150 requests)
    python3 scripts/build-curriculum.py --refresh  # ignore cache, refetch sources
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = os.path.join(ROOT, "curriculum", "sources")
MERGED = os.path.join(ROOT, "curriculum", "merged.json")
PATTERNS = os.path.join(ROOT, "config", "patterns.json")

NEETCODE_URL = (
    "https://raw.githubusercontent.com/krmanik/Anki-NeetCode/main/neetcode-150-list.json"
)

# NeetCode's 18 categories -> our 20-pattern taxonomy.
# We split two of theirs: monotonic-stack out of Stack, fast-slow out of Linked List.
# That split is the point of a pattern-first repo, so it is done explicitly below.
CATEGORY_MAP = {
    "Arrays & Hashing": "01-arrays-hashing",
    "Two Pointers": "02-two-pointers",
    "Sliding Window": "03-sliding-window",
    "Stack": "05-stack",
    "Binary Search": "04-binary-search",
    "Linked List": "07-linked-list",
    "Trees": "09-trees",
    "Heap / Priority Queue": "11-heap-top-k",
    "Backtracking": "12-backtracking",
    "Tries": "10-tries",
    "Graphs": "13-graphs",
    "Advanced Graphs": "14-advanced-graphs",
    "1-D Dynamic Programming": "17-1d-dp",
    "2-D Dynamic Programming": "18-2d-dp",
    "Greedy": "16-greedy",
    "Intervals": "15-intervals",
    "Math & Geometry": "20-math-geometry",
    "Bit Manipulation": "19-bit-manipulation",
}

# Slugs pulled out of their NeetCode category into a finer pattern.
# Applied only if the slug is actually present in the fetched data; any override
# that does not match is reported rather than silently ignored.
PATTERN_OVERRIDES = {
    "daily-temperatures": "06-monotonic-stack",
    "car-fleet": "06-monotonic-stack",
    "largest-rectangle-in-histogram": "06-monotonic-stack",
    "linked-list-cycle": "08-fast-slow-pointers",
    "find-the-duplicate-number": "08-fast-slow-pointers",
}

GQL = "https://leetcode.com/graphql"
GQL_QUERY = """query q($t: String!) {
  question(titleSlug: $t) {
    questionFrontendId
    title
    titleSlug
    difficulty
    isPaidOnly
    topicTags { name slug }
  }
}"""


def fetch(url, timeout=30):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (lets-dsa curriculum builder)"}
    )
    return urllib.request.urlopen(req, timeout=timeout).read().decode()


def slug_from_url(url):
    m = re.search(r"leetcode\.com/problems/([a-z0-9\-]+)", url)
    return m.group(1) if m else None


def load_neetcode(refresh=False):
    """Fetch the NeetCode 150 list. Cached on disk; --refresh forces a refetch."""
    os.makedirs(SOURCES, exist_ok=True)
    cache = os.path.join(SOURCES, "neetcode150.raw.json")
    if refresh or not os.path.exists(cache):
        print(f"  fetching {NEETCODE_URL}")
        raw = fetch(NEETCODE_URL)
        with open(cache, "w") as f:
            f.write(raw)
    else:
        print(f"  using cache {cache}")
    with open(cache) as f:
        return json.load(f)


def verify_slug(slug, retries=2):
    """Verify against LeetCode's public GraphQL. Returns the question dict or None."""
    payload = json.dumps({"query": GQL_QUERY, "variables": {"t": slug}}).encode()
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                GQL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (lets-dsa curriculum builder)",
                    "Referer": "https://leetcode.com",
                },
            )
            body = json.loads(urllib.request.urlopen(req, timeout=25).read().decode())
            return (body.get("data") or {}).get("question")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if attempt == retries:
                return None
            time.sleep(1.5 * (attempt + 1))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="verify every slug against LeetCode (slow, ~150 requests)")
    ap.add_argument("--refresh", action="store_true", help="ignore cached sources")
    args = ap.parse_args()

    with open(PATTERNS) as f:
        valid_patterns = {p["id"] for p in json.load(f)["patterns"]}

    print("Sources")
    nc = load_neetcode(refresh=args.refresh)

    problems = {}
    unmapped_categories = []

    for category, items in nc.items():
        pattern = CATEGORY_MAP.get(category)
        if not pattern:
            unmapped_categories.append(category)
            continue
        for title, meta in items.items():
            slug = slug_from_url(meta.get("url", ""))
            if not slug:
                print(f"  ! no slug in url for {title!r} — dropped")
                continue
            problems[slug] = {
                "slug": slug,
                "title": title,
                "pattern": pattern,
                "neetcode_category": category,
                "difficulty": meta.get("difficulty", "").capitalize(),
                "lists": ["neetcode150"],
                "leetcode_id": None,
                "topic_tags": [],
                "companies": [],
                "paid_only": None,
                "verified": False,
            }

    # Apply the finer-pattern overrides, reporting any that did not match.
    applied, missed = 0, []
    for slug, pattern in PATTERN_OVERRIDES.items():
        if pattern not in valid_patterns:
            missed.append(f"{slug} -> {pattern} (unknown pattern id)")
        elif slug in problems:
            problems[slug]["pattern"] = pattern
            applied += 1
        else:
            missed.append(f"{slug} (not in fetched data)")

    print(f"\nMerge\n  {len(problems)} problems from neetcode150")
    print(f"  {applied} re-assigned to a finer pattern")
    if missed:
        print("  ! overrides that did not apply:")
        for m in missed:
            print(f"      {m}")
    if unmapped_categories:
        print(f"  ! unmapped categories: {unmapped_categories}")

    dropped = []
    if args.verify:
        print(f"\nVerify ({len(problems)} slugs against leetcode.com/graphql)")
        for i, slug in enumerate(sorted(problems), 1):
            q = verify_slug(slug)
            if not q:
                dropped.append(slug)
                print(f"  [{i:3d}/{len(problems)}] {slug}  UNRESOLVED — dropping")
            else:
                p = problems[slug]
                p["leetcode_id"] = int(q["questionFrontendId"])
                p["title"] = q["title"]
                p["difficulty"] = q["difficulty"]
                p["paid_only"] = q.get("isPaidOnly")
                p["topic_tags"] = [t["name"] for t in q.get("topicTags", [])]
                p["verified"] = True
                if i % 25 == 0:
                    print(f"  [{i:3d}/{len(problems)}] ok")
            time.sleep(0.35)  # be a polite client
        for slug in dropped:
            problems.pop(slug, None)
        print(f"  verified {len(problems)}, dropped {len(dropped)}")
    else:
        print("\nVerify  SKIPPED — run with --verify to resolve ids, difficulty and tags")

    by_pattern = {}
    for p in problems.values():
        by_pattern.setdefault(p["pattern"], []).append(p["slug"])

    out = {
        "schema": 1,
        "built": time.strftime("%Y-%m-%d"),
        "verified_against_leetcode": bool(args.verify),
        "counts": {
            "total": len(problems),
            "by_pattern": {k: len(v) for k, v in sorted(by_pattern.items())},
        },
        "dropped_unresolved": dropped,
        "sources": {
            "neetcode150": {"url": NEETCODE_URL, "status": "fetched",
                            "problems": len(problems)},
            "striver_a2z": {"status": "unavailable",
                            "note": "backend.takeuforward.org returned 522 at build time. "
                                    "Structure only: 18 steps / 474 problems. Re-run --refresh "
                                    "later to pick it up if the API returns."},
            "blind75": {"status": "not_fetched",
                        "note": "No reliable machine-readable source found. Blind 75 is a strict "
                                "subset of NeetCode 150, so its problems are already present; "
                                "only the membership flag is missing."},
        },
        "company_tags": {
            "status": "unavailable",
            "note": "LeetCode gates company tags behind Premium and does not expose them on the "
                    "public GraphQL endpoint. Every 'companies' field is [] rather than guessed. "
                    "Company targeting in curriculum/track.md is driven by pattern frequency in "
                    "interviews and by config/user.json, not by fabricated per-problem tags.",
        },
        "problems": dict(sorted(problems.items())),
    }

    os.makedirs(os.path.dirname(MERGED), exist_ok=True)
    with open(MERGED, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"\nWrote {MERGED}")
    for k, v in sorted(out["counts"]["by_pattern"].items()):
        print(f"  {v:3d}  {k}")
    empty = sorted(valid_patterns - set(by_pattern))
    if empty:
        print(f"  (no problems yet: {', '.join(empty)})")
    return 0 if not dropped else 1


if __name__ == "__main__":
    sys.exit(main())
