#!/usr/bin/env python3
"""
build-curriculum.py — assemble the problem curriculum from curated public lists.

This script does not invent problems. Every entry is fetched from a real source and
verified against LeetCode's public GraphQL endpoint, which supplies the canonical id,
title, difficulty and topic tags. A slug that does not resolve is dropped and reported.

Sources
  neetcode150    krmanik/Anki-NeetCode mirror (JSON)          150 problems, 18 categories
  striver_a2z    takeuforward.org (Next.js flight data)       474 problems, 18 steps
  striver_sde    takeuforward.org                             191 problems
  blind75        takeuforward.org                              75 problems
  striver79      takeuforward.org                              79 problems
  codingshuttle  codingshuttle.com (Next.js flight data)      169 problems, all on LeetCode
  lc_striver_sde leetcode.com public list "eeudwo2i"          117 problems, LeetCode-native

Known-unavailable (both render their sheet client-side, nothing in the served HTML):
  geeksforgeeks.org SDE sheet, naukri.com code360 "zero to one" list.

TLS note: on a network with an intercepting corporate proxy, Python may reject the
proxy's CA because Python 3.13+ enables VERIFY_X509_STRICT by default and many corporate
CAs fail its RFC conformance checks. ssl_context() falls back to the macOS system trust
store with that one strictness flag relaxed. Chain and hostname verification stay ON.

Many Striver problems live on GeeksforGeeks or Coding Ninjas rather than LeetCode.
Those cannot be solved through this system's loop, so they are kept separately under
"non_leetcode" instead of being dropped — they still carry sequencing and article value.

Usage:
    python3 scripts/build-curriculum.py            # fetch + merge (uses cache)
    python3 scripts/build-curriculum.py --verify   # also verify every slug (~450 requests)
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

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122 Safari/537.36"

NEETCODE_URL = "https://raw.githubusercontent.com/krmanik/Anki-NeetCode/main/neetcode-150-list.json"
CODINGSHUTTLE_URL = "https://www.codingshuttle.com/sheets/cs-sde-sheet/"
LC_LISTS = {"lc_striver_sde": "eeudwo2i"}

_SSL_CTX = None
_ROOTS = os.path.join(SOURCES, "_system-roots.pem")


def ssl_context():
    """Return a verifying SSL context that also works behind a corporate TLS proxy.

    Tries the default context first. If that cannot verify, rebuilds trust from the
    macOS keychain (where corporate IT installs its root) and clears ONLY
    VERIFY_X509_STRICT -- the RFC-conformance check Python 3.13+ turns on by default and
    which many corporate CAs fail. Certificate chain and hostname verification stay on;
    verification is never disabled.
    """
    global _SSL_CTX
    if _SSL_CTX is not None:
        return _SSL_CTX
    import ssl
    probe = "https://leetcode.com/robots.txt"
    ctx = ssl.create_default_context()
    try:
        urllib.request.urlopen(urllib.request.Request(probe, headers={"User-Agent": UA}),
                               timeout=20, context=ctx)
        _SSL_CTX = ctx
        return ctx
    except Exception as e:
        if "CERTIFICATE_VERIFY_FAILED" not in str(e):
            _SSL_CTX = ctx
            return ctx
        print(f"  TLS   default trust store rejected the connection ({e.__class__.__name__}).")

    os.makedirs(SOURCES, exist_ok=True)
    if not os.path.exists(_ROOTS) or os.path.getsize(_ROOTS) == 0:
        import subprocess
        with open(_ROOTS, "w") as f:
            for kc in ("/System/Library/Keychains/SystemRootCertificates.keychain",
                       "/Library/Keychains/System.keychain"):
                try:
                    f.write(subprocess.run(["security", "find-certificate", "-a", "-p", kc],
                                           capture_output=True, text=True, timeout=60).stdout)
                except Exception:
                    pass
    ctx = ssl.create_default_context(cafile=_ROOTS)
    ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    assert ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname
    print("  TLS   using macOS system trust store; VERIFY_X509_STRICT relaxed "
          "(chain + hostname verification still enforced)")
    _SSL_CTX = ctx
    return ctx

TUF_SHEETS = {
    "striver_a2z": "strivers-a2z-sheet-learn-dsa-a-to-z",
    "striver_sde": "strivers-sde-sheet-top-coding-interview-problems",
    "blind75": "blind-75-leetcode-problems-detailed-video-solutions",
    "striver79": "strivers-79-last-moment-dsa-sheet-ace-interviews",
}

# NeetCode's 18 categories -> our 20-pattern taxonomy. We split two of theirs:
# monotonic-stack out of Stack, fast-slow out of Linked List. That split is the point
# of a pattern-first repo, so it is done explicitly in PATTERN_OVERRIDES below.
CATEGORY_MAP = {
    "Arrays & Hashing": "01-arrays-hashing", "Two Pointers": "02-two-pointers",
    "Sliding Window": "03-sliding-window", "Stack": "05-stack",
    "Binary Search": "04-binary-search", "Linked List": "07-linked-list",
    "Trees": "09-trees", "Heap / Priority Queue": "11-heap-top-k",
    "Backtracking": "12-backtracking", "Tries": "10-tries", "Graphs": "13-graphs",
    "Advanced Graphs": "14-advanced-graphs", "1-D Dynamic Programming": "17-1d-dp",
    "2-D Dynamic Programming": "18-2d-dp", "Greedy": "16-greedy",
    "Intervals": "15-intervals", "Math & Geometry": "20-math-geometry",
    "Bit Manipulation": "19-bit-manipulation",
}

PATTERN_OVERRIDES = {
    "daily-temperatures": "06-monotonic-stack",
    "car-fleet": "06-monotonic-stack",
    "largest-rectangle-in-histogram": "06-monotonic-stack",
    "linked-list-cycle": "08-fast-slow-pointers",
    "find-the-duplicate-number": "08-fast-slow-pointers",
}

# A LeetCode topic tag that is distinctive enough to name a pattern on its own.
# Checked before the broader overlap score. Grounded in real tags from the API,
# never in a guess about what the problem "feels like".
SIGNATURE_TAGS = {
    "Sliding Window": "03-sliding-window", "Monotonic Stack": "06-monotonic-stack",
    "Trie": "10-tries", "Backtracking": "12-backtracking",
    "Bit Manipulation": "19-bit-manipulation", "Binary Search": "04-binary-search",
    "Union Find": "14-advanced-graphs", "Shortest Path": "14-advanced-graphs",
    "Minimum Spanning Tree": "14-advanced-graphs", "Topological Sort": "13-graphs",
    "Heap (Priority Queue)": "11-heap-top-k", "Linked List": "07-linked-list",
    "Binary Search Tree": "09-trees", "Trees": "09-trees",
    "Dynamic Programming": "17-1d-dp", "Greedy": "16-greedy",
}

GQL = "https://leetcode.com/graphql"
GQL_QUERY = """query q($t: String!) {
  question(titleSlug: $t) {
    questionFrontendId title titleSlug difficulty isPaidOnly
    topicTags { name }
  }
}"""


def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout,
                                  context=ssl_context()).read().decode("utf-8", "replace")


def gql(query, variables, timeout=25):
    req = urllib.request.Request(GQL, data=json.dumps(
        {"query": query, "variables": variables}).encode(), headers={
        "Content-Type": "application/json", "User-Agent": UA,
        "Referer": "https://leetcode.com"})
    return json.loads(urllib.request.urlopen(
        req, timeout=timeout, context=ssl_context()).read().decode())


def cached(name, url, refresh):
    os.makedirs(SOURCES, exist_ok=True)
    path = os.path.join(SOURCES, name)
    if refresh or not os.path.exists(path):
        print(f"  fetching {url}")
        with open(path, "w") as f:
            f.write(fetch(url))
    else:
        print(f"  cache    {name}")
    with open(path) as f:
        return f.read()


def slug_from_url(url):
    if not isinstance(url, str):
        return None
    m = re.search(r"leetcode\.com/problems/([a-zA-Z0-9\-]+)", url)
    return m.group(1).lower() if m else None


# ---------- takeuforward: Next.js flight data ----------

def flight_payload(html):
    """Reassemble the RSC flight payload. It is split mid-string across many pushes,
    so the raw fragments must be concatenated BEFORE unescaping."""
    parts = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.S)
    if not parts:
        return None
    return json.loads('"' + "".join(parts) + '"')


def extract_array(payload, key, start=0):
    """Find "<key>":[ ... ] and bracket-match to its close, respecting strings."""
    i = payload.find(f'"{key}":', start)
    if i == -1:
        return None
    j = payload.index("[", i)
    depth = 0
    instr = esc = False
    for k in range(j, len(payload)):
        c = payload[k]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
            continue
        if c == '"':
            instr = True
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return json.loads(payload[j:k + 1])
    return None


def extract_sections(payload):
    return extract_array(payload, "sections")


def parse_codingshuttle(html):
    """CodingShuttle ships a flat problems array in its flight payload:
    {id, title, topic, difficulty, avgTimeMins, url}. Every url is a LeetCode link."""
    payload = flight_payload(html)
    if payload is None:
        raise ValueError("no flight payload — page shape changed")
    best = []
    start = 0
    while True:  # several "problems" keys exist; keep the largest array
        i = payload.find('"problems":', start)
        if i == -1:
            break
        arr = extract_array(payload, "problems", start)
        if arr and len(arr) > len(best):
            best = arr
        start = i + 11
    if not best:
        raise ValueError('no "problems" array — page shape changed')
    return [{
        "name": r.get("title"), "step_no": 1, "step": r.get("topic") or "",
        "substep": None, "difficulty": (r.get("difficulty") or "").capitalize(),
        "leetcode": r.get("url"), "article": None, "youtube": None,
        "avg_time_mins": r.get("avgTimeMins"),
    } for r in best if isinstance(r, dict)]


LC_LIST_QUERY = """query($favoriteSlug: String!, $limit: Int, $skip: Int) {
  favoriteQuestionList(favoriteSlug: $favoriteSlug, limit: $limit, skip: $skip) {
    totalLength
    questions { title titleSlug difficulty questionFrontendId paidOnly
                topicTags { name } }
  }
}"""


def fetch_leetcode_list(fav_slug):
    """A public LeetCode problem list. Paginated, and already carries real ids,
    difficulty, paidOnly and topic tags — no separate verification needed."""
    rows, skip, total = [], 0, None
    while total is None or skip < total:
        body = gql(LC_LIST_QUERY, {"favoriteSlug": fav_slug, "limit": 100, "skip": skip})
        node = (body.get("data") or {}).get("favoriteQuestionList")
        if not node:
            raise ValueError(f"list {fav_slug} returned no data")
        total = node["totalLength"]
        batch = node.get("questions") or []
        if not batch:
            break
        for q in batch:
            rows.append({
                "name": q["title"], "step_no": 1, "step": "", "substep": None,
                "difficulty": (q["difficulty"] or "").capitalize(),
                "leetcode": f"https://leetcode.com/problems/{q['titleSlug']}/",
                "article": None, "youtube": None,
                "_id": int(q["questionFrontendId"]),
                "_paid": q.get("paidOnly"),
                "_tags": [t["name"] for t in (q.get("topicTags") or [])],
            })
        skip += len(batch)
        time.sleep(0.3)
    return rows


def parse_tuf(html):
    """Normalize both shapes: nested (category -> subcategories -> problems) as in A2Z,
    and flat (category -> problems) as in the SDE sheet."""
    payload = flight_payload(html)
    if payload is None:
        raise ValueError("no flight payload — page shape changed")
    sections = extract_sections(payload)
    if sections is None:
        raise ValueError('no "sections" key — page shape changed')

    rows = []
    for n, cat in enumerate(sections, 1):
        cname = cat.get("category_name", "")
        groups = cat.get("subcategories")
        if groups is None:
            groups = [{"subcategory_name": None, "problems": cat.get("problems", [])}]
        for grp in groups:
            for p in grp.get("problems", []):
                def clean(v):
                    return v if isinstance(v, str) and v.startswith("http") else None
                rows.append({
                    "name": p.get("problem_name"),
                    "step_no": n,
                    "step": cname,
                    "substep": grp.get("subcategory_name"),
                    "difficulty": p.get("difficulty"),
                    "leetcode": clean(p.get("leetcode")),
                    "article": clean(p.get("article")),
                    "youtube": clean(p.get("youtube")),
                })
    return rows


# ---------- verification ----------

def verify_slug(slug, retries=2):
    payload = json.dumps({"query": GQL_QUERY, "variables": {"t": slug}}).encode()
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(GQL, data=payload, headers={
                "Content-Type": "application/json", "User-Agent": UA,
                "Referer": "https://leetcode.com"})
            body = json.loads(urllib.request.urlopen(
                req, timeout=25, context=ssl_context()).read().decode())
            return (body.get("data") or {}).get("question")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            if attempt == retries:
                return None
            time.sleep(1.5 * (attempt + 1))
    return None


def infer_pattern(tags, pattern_tags):
    """Assign a pattern from real LeetCode topic tags. Signature tag first, then the
    best overlap. Returns (pattern_id, how) or (None, 'unassigned')."""
    for t in tags:
        if t in SIGNATURE_TAGS:
            return SIGNATURE_TAGS[t], "leetcode-tags:signature"
    best, score = None, 0
    for pid, ptags in pattern_tags.items():
        n = len(set(tags) & set(ptags))
        if n > score:
            best, score = pid, n
    return (best, "leetcode-tags:overlap") if best else (None, "unassigned")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()

    with open(PATTERNS) as f:
        pj = json.load(f)["patterns"]
    valid_patterns = {p["id"] for p in pj}
    pattern_tags = {p["id"]: p.get("leetcode_tags", []) for p in pj}

    print("Sources")
    problems, non_leetcode, source_report = {}, [], {}

    # --- NeetCode 150 ---
    try:
        nc = json.loads(cached("neetcode150.raw.json", NEETCODE_URL, args.refresh))
        n = 0
        for category, items in nc.items():
            pattern = CATEGORY_MAP.get(category)
            for title, meta in items.items():
                slug = slug_from_url(meta.get("url", ""))
                if not slug:
                    continue
                problems[slug] = {
                    "slug": slug, "title": title, "pattern": pattern,
                    "pattern_source": "neetcode" if pattern else "unassigned",
                    "neetcode_category": category,
                    "difficulty": (meta.get("difficulty") or "").capitalize(),
                    "lists": ["neetcode150"], "leetcode_id": None, "topic_tags": [],
                    "companies": [], "paid_only": None, "verified": False,
                    "resources": {}, "striver": None,
                }
                n += 1
        source_report["neetcode150"] = {"url": NEETCODE_URL, "status": "fetched", "problems": n}
        print(f"           neetcode150   {n} problems")
    except Exception as e:
        source_report["neetcode150"] = {"status": "failed", "error": str(e)}
        print(f"  ! neetcode150 FAILED: {e}")

    # --- shared absorber: every source normalizes to the same row shape ---
    def absorb(key, rows):
        on_lc = 0
        for r in rows:
            slug = slug_from_url(r.get("leetcode"))
            if not slug:
                non_leetcode.append({
                    "name": r.get("name"), "list": key, "step_no": r.get("step_no"),
                    "step": r.get("step"), "substep": r.get("substep"),
                    "difficulty": r.get("difficulty"), "article": r.get("article"),
                    "youtube": r.get("youtube"),
                })
                continue
            on_lc += 1
            p = problems.get(slug)
            if not p:
                p = problems[slug] = {
                    "slug": slug, "title": r.get("name"), "pattern": None,
                    "pattern_source": "unassigned", "neetcode_category": None,
                    "difficulty": r.get("difficulty"), "lists": [], "leetcode_id": None,
                    "topic_tags": [], "companies": [], "paid_only": None,
                    "verified": False, "resources": {}, "striver": None,
                }
            if key not in p["lists"]:
                p["lists"].append(key)
            # Striver's own teaching resources — genuinely useful, and free.
            if r.get("article") and "article" not in p["resources"]:
                p["resources"]["article"] = r["article"]
            if r.get("youtube") and "youtube" not in p["resources"]:
                p["resources"]["youtube"] = r["youtube"]
            if key == "striver_a2z" and not p["striver"]:
                p["striver"] = {"step_no": r["step_no"], "step": r["step"],
                                "substep": r["substep"]}
            if r.get("avg_time_mins") and not p.get("avg_time_mins"):
                p["avg_time_mins"] = r["avg_time_mins"]
            # A LeetCode list already carries authoritative fields.
            if r.get("_id"):
                p["leetcode_id"] = p["leetcode_id"] or r["_id"]
                if r.get("_tags") and not p["topic_tags"]:
                    p["topic_tags"] = r["_tags"]
                if p["paid_only"] is None:
                    p["paid_only"] = r.get("_paid")
        return on_lc

    # --- the four takeuforward sheets ---
    for key, path_slug in TUF_SHEETS.items():
        url = f"https://takeuforward.org/dsa/{path_slug}"
        try:
            rows = parse_tuf(cached(f"{key}.raw.html", url, args.refresh))
        except Exception as e:
            source_report[key] = {"url": url, "status": "failed", "error": str(e)}
            print(f"  ! {key} FAILED: {e}")
            continue
        on_lc = absorb(key, rows)
        source_report[key] = {"url": url, "status": "fetched", "problems": len(rows),
                              "on_leetcode": on_lc, "not_on_leetcode": len(rows) - on_lc}
        print(f"           {key:15s} {len(rows)} problems, {on_lc} on leetcode")

    # --- CodingShuttle CS SDE sheet ---
    try:
        rows = parse_codingshuttle(cached("codingshuttle.raw.html", CODINGSHUTTLE_URL,
                                          args.refresh))
        on_lc = absorb("codingshuttle", rows)
        source_report["codingshuttle"] = {"url": CODINGSHUTTLE_URL, "status": "fetched",
                                          "problems": len(rows), "on_leetcode": on_lc,
                                          "not_on_leetcode": len(rows) - on_lc}
        print(f"           {'codingshuttle':15s} {len(rows)} problems, {on_lc} on leetcode")
    except Exception as e:
        source_report["codingshuttle"] = {"url": CODINGSHUTTLE_URL, "status": "failed",
                                          "error": str(e)}
        print(f"  ! codingshuttle FAILED: {e}")

    # --- public LeetCode problem lists ---
    for key, fav in LC_LISTS.items():
        url = f"https://leetcode.com/problem-list/{fav}/"
        try:
            rows = fetch_leetcode_list(fav)
            on_lc = absorb(key, rows)
            source_report[key] = {"url": url, "status": "fetched",
                                  "problems": len(rows), "on_leetcode": on_lc,
                                  "note": "LeetCode-native list; ids, tags and paidOnly "
                                          "come straight from the API"}
            print(f"           {key:15s} {len(rows)} problems, {on_lc} on leetcode")
        except Exception as e:
            source_report[key] = {"url": url, "status": "failed", "error": str(e)}
            print(f"  ! {key} FAILED: {e}")

    # --- sources that cannot be fetched at all ---
    source_report["geeksforgeeks_sde"] = {
        "url": "https://www.geeksforgeeks.org/dsa/sde-sheet-a-complete-guide-for-sde-preparation/",
        "status": "unavailable",
        "note": "Sheet is rendered client-side; the served HTML contains zero problem links. "
                "Would need a headless browser. Low marginal value — GfG's SDE sheet is "
                "substantially the same list as striver_sde, which is already merged."}
    source_report["naukri_code360"] = {
        "url": "https://www.naukri.com/code360/problem-lists/zero-to-one-sde-sheet",
        "status": "unavailable",
        "note": "21KB JS shell, no data in the served HTML. Its problems are hosted on "
                "Code360 rather than LeetCode, so they could not run through the S0-S6 "
                "loop (which ends in a LeetCode submission) even if fetched."}

    # --- finer-pattern overrides ---
    applied, missed = 0, []
    for slug, pattern in PATTERN_OVERRIDES.items():
        if pattern not in valid_patterns:
            missed.append(f"{slug} -> {pattern} (unknown pattern id)")
        elif slug in problems:
            problems[slug]["pattern"] = pattern
            problems[slug]["pattern_source"] = "override"
            applied += 1
        else:
            missed.append(f"{slug} (not in fetched data)")

    print(f"\nMerge\n  {len(problems)} unique problems on LeetCode")
    print(f"  {len(non_leetcode)} problems not on LeetCode (kept under 'non_leetcode')")
    print(f"  {applied} re-assigned to a finer pattern")
    for m in missed:
        print(f"  ! override did not apply: {m}")

    # --- verification ---
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
                if not p["pattern"]:
                    p["pattern"], p["pattern_source"] = infer_pattern(
                        p["topic_tags"], pattern_tags)
                if i % 50 == 0:
                    print(f"  [{i:3d}/{len(problems)}] ok")
            time.sleep(0.25)
        for slug in dropped:
            problems.pop(slug, None)
        print(f"  verified {len(problems)}, dropped {len(dropped)}")
    else:
        print("\nVerify  SKIPPED — run with --verify to resolve ids, tags and patterns")

    by_pattern, by_list, by_source = {}, {}, {}
    for p in problems.values():
        by_pattern.setdefault(p["pattern"] or "UNASSIGNED", []).append(p["slug"])
        by_source[p["pattern_source"]] = by_source.get(p["pattern_source"], 0) + 1
        for l in p["lists"]:
            by_list[l] = by_list.get(l, 0) + 1

    out = {
        "schema": 2,
        "built": time.strftime("%Y-%m-%d"),
        "verified_against_leetcode": bool(args.verify),
        "counts": {
            "total": len(problems),
            "non_leetcode": len(non_leetcode),
            "by_pattern": {k: len(v) for k, v in sorted(by_pattern.items())},
            "by_list": dict(sorted(by_list.items())),
            "by_pattern_source": dict(sorted(by_source.items())),
        },
        "dropped_unresolved": dropped,
        "sources": source_report,
        "pattern_assignment": {
            "neetcode": "pattern taken from the NeetCode category (pattern-first by design)",
            "override": "hand-split into a finer pattern — see PATTERN_OVERRIDES in the script",
            "leetcode-tags:signature": "a distinctive real LeetCode topic tag named the pattern",
            "leetcode-tags:overlap": "best overlap between real topic tags and config/patterns.json",
            "unassigned": "no confident assignment — left null rather than guessed",
        },
        "company_tags": {
            "status": "unavailable",
            "note": "LeetCode gates company tags behind Premium and does not expose them on the "
                    "public GraphQL endpoint. Every 'companies' field is [] rather than guessed. "
                    "Company targeting in curriculum/track.md is driven by list membership "
                    "(blind75 and striver79 are the interview-frequency signals) and by "
                    "config/user.json — not by fabricated per-problem tags.",
        },
        "problems": dict(sorted(problems.items())),
        "non_leetcode": sorted(non_leetcode, key=lambda r: (r["list"], r["step_no"], r["name"] or "")),
    }

    os.makedirs(os.path.dirname(MERGED), exist_ok=True)
    with open(MERGED, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"\nWrote {MERGED}")
    for k, v in sorted(out["counts"]["by_pattern"].items()):
        print(f"  {v:4d}  {k}")
    print("  lists:", out["counts"]["by_list"])
    empty = sorted(valid_patterns - set(by_pattern))
    if empty:
        print(f"  (no problems yet: {', '.join(empty)})")
    return 0 if not dropped else 1


if __name__ == "__main__":
    sys.exit(main())
