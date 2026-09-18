#!/usr/bin/env python3
"""
roll-stats.py — recompute state/stats.json from question frontmatter.

The SINGLE writer of state/stats.json. Nothing else should write that file.

Mastery is deliberately not a solve count. A problem solved at hint rung 5 after four
attempts is not the same as one solved cold, and a report that treats them alike will
tell the learner they are ready when they are not.
"""

import glob
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS = os.path.join(ROOT, "questions")
STATS = os.path.join(ROOT, "state", "stats.json")
PATTERNS = os.path.join(ROOT, "config", "patterns.json")
MERGED = os.path.join(ROOT, "curriculum", "merged.json")


def parse_frontmatter(path):
    """Minimal YAML frontmatter reader — flat scalars only, which is all we write."""
    try:
        with open(path) as f:
            text = f.read()
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip().strip('"').strip("'")
        if v in ("null", "", "~"):
            fm[k.strip()] = None
        elif v.lower() in ("true", "false"):
            fm[k.strip()] = v.lower() == "true"
        elif v.lstrip("-").isdigit():
            fm[k.strip()] = int(v)
        else:
            fm[k.strip()] = v
    return fm


def band(solved, avg_hints, revisit_passed):
    if solved == 0:
        return "untouched"
    if solved >= 3 and avg_hints <= 1.0 and revisit_passed:
        return "solid"
    if solved >= 2 and avg_hints <= 3.0:
        return "working"
    return "exposed"


def main():
    with open(PATTERNS) as f:
        patterns = {p["id"]: p["name"] for p in json.load(f)["patterns"]}

    available = {}
    if os.path.exists(MERGED):
        with open(MERGED) as f:
            for p in json.load(f)["problems"].values():
                available[p["pattern"]] = available.get(p["pattern"], 0) + 1

    today = date.today().isoformat()
    per = {pid: {"pattern": pid, "name": name, "available": available.get(pid, 0),
                 "solved": 0, "in_progress": 0, "hints_total": 0, "attempts_total": 0,
                 "ramp_overrides": 0, "review_only": 0, "interview": 0,
                 "revisit_passed": False, "due_now": []}
           for pid, name in patterns.items()}

    unknown_pattern = []
    due, parsed = [], 0

    for path in sorted(glob.glob(os.path.join(QUESTIONS, "*", "*.md"))):
        fm = parse_frontmatter(path)
        if not fm:
            continue
        parsed += 1
        pid = fm.get("pattern")
        if pid not in per:
            unknown_pattern.append(os.path.relpath(path, ROOT))
            continue
        rec = per[pid]
        status = fm.get("status")
        mode = fm.get("mode") or "teach"

        if mode == "review-only":
            rec["review_only"] += 1
            continue  # did not go through the loop — does not count toward mastery
        if mode == "interview":
            rec["interview"] += 1
            continue  # tracked separately so it does not inflate teaching stats

        if status == "solved":
            rec["solved"] += 1
            rec["hints_total"] += fm.get("hints_used") or 0
            rec["attempts_total"] += fm.get("attempts") or 0
            if fm.get("ramp_override"):
                rec["ramp_overrides"] += 1
            if fm.get("revisit_passed_cold"):
                rec["revisit_passed"] = True
            r = fm.get("revisit_on")
            if r and r <= today:
                rec["due_now"].append(fm.get("problem") or os.path.basename(path))
                due.append({"problem": fm.get("problem"), "pattern": pid,
                            "revisit_on": r, "path": os.path.relpath(path, ROOT)})
        elif status in ("in-progress", "parked"):
            rec["in_progress"] += 1

    for rec in per.values():
        s = rec["solved"]
        rec["avg_hints"] = round(rec["hints_total"] / s, 2) if s else None
        rec["avg_attempts"] = round(rec["attempts_total"] / s, 2) if s else None
        rec["band"] = band(s, rec["avg_hints"] if s else 99, rec["revisit_passed"])
        rec.pop("hints_total"), rec.pop("attempts_total")

    bands = {b: sum(1 for r in per.values() if r["band"] == b)
             for b in ("solid", "working", "exposed", "untouched")}
    total_solved = sum(r["solved"] for r in per.values())
    touched = sum(1 for r in per.values() if r["solved"] or r["in_progress"])

    out = {
        "schema": 1,
        "generated": today,
        "generated_by": "scripts/roll-stats.py",
        "totals": {
            "solved": total_solved,
            "available": sum(available.values()) or None,
            "patterns_touched": touched,
            "patterns_total": len(patterns),
            "review_only": sum(r["review_only"] for r in per.values()),
            "interview_runs": sum(r["interview"] for r in per.values()),
        },
        "bands": bands,
        "due_for_revisit": sorted(due, key=lambda d: d["revisit_on"]),
        "patterns": [per[k] for k in sorted(per)],
        "warnings": ({"unknown_pattern_in_files": unknown_pattern} if unknown_pattern else {}),
    }

    os.makedirs(os.path.dirname(STATS), exist_ok=True)
    with open(STATS, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"solved: {total_solved} · patterns touched: {touched}/{len(patterns)}")
    print(f"solid: {bands['solid']} · working: {bands['working']} · "
          f"exposed: {bands['exposed']} · untouched: {bands['untouched']}")
    print(f"due for revisit: {len(due)}")
    print(f"parsed {parsed} question files -> {STATS}")
    if unknown_pattern:
        print(f"! files with an unknown pattern id: {unknown_pattern}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
