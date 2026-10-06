#!/usr/bin/env python3
"""
next-problem.py -- decide WHICH problem `next` serves and in WHICH S1 mode.

Two modes, because "name the pattern" only tests anything when the learner does not
already know the answer:

  learn     The problem is in the pattern they are currently working through. The pattern
            is TOLD (in the S0 header and the brief). The S1 gate asks for the SIGNAL: which
            line of the problem makes this the right tool, and what breaks if they try the
            obvious approach. Asking them to "name" a pattern printed in the header, or
            taught a minute ago, is a giveaway or a parroting exercise.

  identify  The problem is drawn from an EARLIER pattern, out of sequence. The pattern is
            HIDDEN (`Pattern: ?`), and the gate asks which of the patterns they have met
            fits, and what in the statement says so. This is the only place recognition is
            actually exercised -- the track is blocked by pattern, and blocked practice never
            makes anyone tell problems apart. Interviews are fully interleaved.

The interleave rule is deterministic so a small model cannot drift on it:
once 3+ patterns are `working` or `solid`, every third problem (solved % 3 == 2) comes
from an earlier pattern -- the one whose last solve is OLDEST, since that is the one most
at risk of being forgotten.

Read-only. Prints a line for humans; --json for skills.

Usage:
    python3 scripts/next-problem.py            # what `next` should serve
    python3 scripts/next-problem.py --json
    python3 scripts/next-problem.py --revisit two-sum --json   # mode for a revisit
"""

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACK = os.path.join(ROOT, "curriculum", "track.md")
MERGED = os.path.join(ROOT, "curriculum", "merged.json")
STATS = os.path.join(ROOT, "state", "stats.json")
PATTERNS = os.path.join(ROOT, "config", "patterns.json")
QUESTIONS = os.path.join(ROOT, "questions")

INTERLEAVE_EVERY = 3        # one problem in three, once the gate below is met
INTERLEAVE_MIN_PATTERNS = 3  # a menu of fewer than three known patterns is a giveaway
DIFF = {"Easy": 0, "Medium": 1, "Hard": 2}


def frontmatter(path):
    try:
        text = open(path).read()
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def touched():
    """slug -> frontmatter, for every problem with a question file (solved or not)."""
    out = {}
    for p in glob.glob(os.path.join(QUESTIONS, "*", "*.md")):
        fm = frontmatter(p)
        out[fm.get("problem") or os.path.basename(p)[:-3]] = fm
    return out


def track_rows():
    """(pattern_id, slug) in track order, plus each pattern's advance quota. The track is
    the authority on both; this only reads it."""
    rows, quota, pid = [], {}, None
    for line in open(TRACK):
        m = re.match(r"## .+?`([0-9]{2}-[a-z0-9-]+)`", line)
        if m:
            pid = m.group(1)
            continue
        q = re.search(r"solve (\d+) to advance", line)
        if pid and q:
            quota[pid] = int(q.group(1))
        m = re.search(r"leetcode\.com/problems/([a-z0-9-]+)/", line)
        if pid and line.startswith("| [") and m:
            rows.append((pid, m.group(1)))
    return rows, quota


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--revisit", metavar="SLUG", help="report the mode for a revisit instead")
    a = ap.parse_args()

    for f in (TRACK, MERGED, STATS, PATTERNS):
        if not os.path.exists(f):
            print(f"! {os.path.relpath(f, ROOT)} missing", file=sys.stderr)
            return 1

    names = {p["id"]: p["name"] for p in json.load(open(PATTERNS))["patterns"]}
    stats = json.load(open(STATS))
    bands = {r["pattern"]: r["band"] for r in stats.get("patterns", [])}
    merged = json.load(open(MERGED))["problems"]
    merged = merged if isinstance(merged, dict) else {p["slug"]: p for p in merged}
    done = touched()
    solved = [s for s, fm in done.items() if fm.get("status") == "solved"]

    held = [p for p, b in bands.items() if b in ("working", "solid")]
    met = [p for p, b in bands.items() if b != "untouched"]

    def menu():
        return sorted(names[p] for p in met)

    def result(slug, pid, mode, why):
        m = merged.get(slug, {})
        r = {"slug": slug, "title": m.get("title", slug), "leetcode_id": m.get("leetcode_id"),
             "difficulty": m.get("difficulty"), "pattern": pid, "pattern_name": names.get(pid),
             "s1_mode": mode, "why": why}
        if mode == "identify":
            r["menu"] = menu()
            r["header_pattern"] = "?"
        else:
            r["header_pattern"] = names.get(pid)
        return r

    # ---- a revisit: identify mode when the menu is big enough to mean something ----
    if a.revisit:
        pid = done.get(a.revisit, {}).get("pattern") or merged.get(a.revisit, {}).get("pattern")
        mode = "identify" if len(met) >= INTERLEAVE_MIN_PATTERNS else "learn"
        why = ("revisit, pattern hidden" if mode == "identify" else
               f"revisit, but only {len(met)} pattern(s) met -- a menu that small gives it away")
        out = result(a.revisit, pid, mode, why)
        print(json.dumps(out, indent=2) if a.json else f"{out['title']} · {mode} · {why}")
        return 0

    rows, quota = track_rows()
    solved_in = {}
    for s in solved:
        p = done[s].get("pattern")
        solved_in[p] = solved_in.get(p, 0) + 1
    # A pattern whose advance quota is met is finished for ladder purposes. Without this,
    # "first unstarted row" kept serving Hards in a pattern the learner had already cleared.
    fresh = [(p, s) for p, s in rows
             if s not in done and solved_in.get(p, 0) < quota.get(p, 10**6)]
    if not fresh:
        print("! nothing left unstarted in curriculum/track.md", file=sys.stderr)
        return 1
    cur_pid, cur_slug = fresh[0]

    interleave = (len(held) >= INTERLEAVE_MIN_PATTERNS
                  and len(solved) % INTERLEAVE_EVERY == INTERLEAVE_EVERY - 1)

    if interleave:
        # The earlier held pattern whose most recent solve is oldest -- most at risk.
        last = {}
        for s, fm in done.items():
            if fm.get("status") == "solved" and fm.get("pattern"):
                last[fm["pattern"]] = max(last.get(fm["pattern"], ""), fm.get("solved_on") or "")
        earlier = sorted((p for p in held if p != cur_pid), key=lambda p: last.get(p, ""))
        for pid in earlier:
            cands = [s for p, s in rows if p == pid and s not in done]
            if not cands:  # track rows exhausted -- fall back to the full pattern
                pool = [m for m in merged.values()
                        if m.get("pattern") == pid and m["slug"] not in done
                        and not m.get("paid_only")]
                pool.sort(key=lambda m: (DIFF.get(m.get("difficulty"), 3),
                                         -len(m.get("lists") or []), m.get("leetcode_id") or 0))
                cands = [m["slug"] for m in pool]
            if cands:
                out = result(cands[0], pid, "identify",
                             f"interleaved: every {INTERLEAVE_EVERY}rd problem comes from an "
                             f"earlier pattern; {names[pid]} has gone longest without practice")
                print(json.dumps(out, indent=2) if a.json else
                      f"{out['title']} · identify · {out['why']}")
                return 0
        # every earlier pattern exhausted -- fall through to the track

    why = ("next in your current pattern" if not interleave else
           "would have interleaved, but no earlier pattern has an unstarted problem")
    if len(held) < INTERLEAVE_MIN_PATTERNS:
        why += (f" · interleaving starts once {INTERLEAVE_MIN_PATTERNS} patterns are working "
                f"(you have {len(held)})")
    out = result(cur_slug, cur_pid, "learn", why)
    print(json.dumps(out, indent=2) if a.json else f"{out['title']} · learn · {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
