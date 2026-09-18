#!/usr/bin/env python3
"""
status.py — read-only snapshot of where the learner is.

Called at session start so Claude gets one JSON blob instead of stat-ing files itself.
Writes nothing. Never fails hard: a missing file becomes a null and a note, because a
crashing status script at session start is worse than an incomplete one.
"""

import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return {"_error": f"{rel}: {e}"}


def main():
    user = read("config/user.json")
    current = read("state/current.json")
    stats = read("state/stats.json")
    merged = read("curriculum/merged.json")

    gates = []
    if not user:
        gates.append("config/user.json missing — run skills/setup")
    if not merged:
        gates.append("curriculum/merged.json missing — run scripts/build-curriculum.py")
    elif not merged.get("verified_against_leetcode"):
        gates.append("curriculum built but unverified — rerun with --verify")
    if not os.path.exists(os.path.join(ROOT, "curriculum", "track.md")):
        gates.append("curriculum/track.md missing — generate it in setup phase 5")
    if not current:
        gates.append("state/current.json missing — run skills/setup")

    active = (current or {}).get("active")
    out = {
        "generated": date.today().isoformat(),
        "setup_gates_failing": gates,
        "ready": not gates,
        "level": (user or {}).get("level"),
        "target_companies": (user or {}).get("target_companies", []),
        "timeline_weeks": (user or {}).get("timeline_weeks"),
        "daily_budget": (user or {}).get("daily_budget_problems"),
        "active": active,
        "parked_count": len((current or {}).get("parked", [])),
        "counters": (current or {}).get("counters", {}),
        "solved": ((stats or {}).get("totals") or {}).get("solved", 0),
        "patterns_touched": ((stats or {}).get("totals") or {}).get("patterns_touched", 0),
        "bands": (stats or {}).get("bands", {}),
        "due_for_revisit": len((stats or {}).get("due_for_revisit", [])),
        "curriculum_problems": ((merged or {}).get("counts") or {}).get("total", 0),
        "stats_stale": _stale(stats),
    }
    print(json.dumps(out, indent=2))
    return 0


def _stale(stats):
    """True if any question file is newer than stats.json — the report would be wrong."""
    sp = os.path.join(ROOT, "state", "stats.json")
    if not stats or not os.path.exists(sp):
        return True
    smt = os.path.getmtime(sp)
    qdir = os.path.join(ROOT, "questions")
    for root, _, files in os.walk(qdir):
        for fn in files:
            if fn.endswith(".md") and os.path.getmtime(os.path.join(root, fn)) > smt:
                return True
    return False


if __name__ == "__main__":
    sys.exit(main())
