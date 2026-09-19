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
TOPICS_DIR = os.path.join(ROOT, "topics")
FOUNDATIONS = os.path.join(ROOT, "config", "foundations.json")
STATS = os.path.join(ROOT, "state", "stats.json")
PATTERNS = os.path.join(ROOT, "config", "patterns.json")
MERGED = os.path.join(ROOT, "curriculum", "merged.json")
LEDGER = os.path.join(ROOT, "state", "oa-attempts.json")
# Advancement floors per dependency tier, mirroring TIER_RULES in build-track.py.
TIER_FLOOR = {1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 3}
READINESS = {"floor": 90, "interview": 180, "strong": 250}


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


def slug_of(fm, path):
    return fm.get("problem") or os.path.basename(path)[:-3]


def read_oa():
    """OA attempts are evidence of coding under pressure. They were being written and
    read by nothing, so four submissions counted toward no metric at all."""
    if not os.path.exists(LEDGER):
        return None
    try:
        rows = json.load(open(LEDGER)).get("attempts", [])
    except (json.JSONDecodeError, OSError):
        return None
    if not rows:
        return None
    by_problem = {}
    for a in rows:
        by_problem.setdefault(a["problem"], []).append(a)
    firsts = [sorted(v, key=lambda x: x.get("attempt", 0))[0] for v in by_problem.values()]
    accepted = [v for v in by_problem.values()
                if any(a.get("verdict") == "accepted" for a in v)]
    times = [min((a.get("elapsed_s") or 0) for a in v
                 if a.get("verdict") == "accepted") for v in accepted] or [0]
    langs = {}
    for a in rows:
        langs[a.get("lang")] = langs.get(a.get("lang"), 0) + 1
    return {
        "attempts": len(rows),
        "problems_attempted": len(by_problem),
        "problems_accepted": len(accepted),
        "compiled_first_try": sum(1 for a in firsts if a.get("compiled")),
        "compile_first_try_rate": round(
            sum(1 for a in firsts if a.get("compiled")) / len(firsts), 2),
        "accepted_first_submit": sum(
            1 for a in firsts if a.get("verdict") == "accepted"),
        "avg_attempts_to_accept": round(
            sum(len(v) for v in accepted) / len(accepted), 2) if accepted else None,
        "median_time_to_accept_s": sorted(times)[len(times) // 2] if accepted else None,
        "languages": langs,
    }


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

    available, meta = {}, {}
    if os.path.exists(MERGED):
        with open(MERGED) as f:
            for p in json.load(f)["problems"].values():
                available[p["pattern"]] = available.get(p["pattern"], 0) + 1
                meta[p["slug"]] = p

    today = date.today().isoformat()
    per = {pid: {"pattern": pid, "name": name, "available": available.get(pid, 0),
                 "solved": 0, "in_progress": 0, "hints_total": 0, "attempts_total": 0,
                 "ramp_overrides": 0, "review_only": 0, "interview": 0,
                 "revisit_passed": False, "due_now": []}
           for pid, name in patterns.items()}

    unknown_pattern = []
    due, parsed = [], 0
    by_difficulty = {"Easy": 0, "Medium": 0, "Hard": 0}
    companies_solved, solved_slugs = {}, []

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
            m = meta.get(slug_of(fm, path))
            if m:
                solved_slugs.append(m["slug"])
                if m.get("difficulty") in by_difficulty:
                    by_difficulty[m["difficulty"]] += 1
                for c in (m.get("companies") or []):
                    companies_solved[c] = companies_solved.get(c, 0) + 1
            rec["hints_total"] += fm.get("hints_used") or 0
            rec["attempts_total"] += fm.get("attempts") or 0
            if fm.get("ramp_override"):
                rec["ramp_overrides"] += 1
            if fm.get("revisit_passed_cold"):
                rec["revisit_passed"] = True
            # srs_due is authoritative (scripts/schedule.py). revisit_on is kept only as a
            # mirror for anything written before the scheduler existed.
            r = fm.get("srs_due") or fm.get("revisit_on")
            if r and r <= today:
                rec["due_now"].append(fm.get("problem") or os.path.basename(path))
                due.append({"problem": fm.get("problem"), "pattern": pid,
                            "revisit_on": r, "lapses": fm.get("srs_lapses") or 0,
                            "stability": fm.get("srs_stability"),
                            "path": os.path.relpath(path, ROOT)})
        elif status in ("in-progress", "parked"):
            rec["in_progress"] += 1

    for rec in per.values():
        s = rec["solved"]
        rec["avg_hints"] = round(rec["hints_total"] / s, 2) if s else None
        rec["avg_attempts"] = round(rec["attempts_total"] / s, 2) if s else None
        rec["band"] = band(s, rec["avg_hints"] if s else 99, rec["revisit_passed"])
        rec.pop("hints_total"), rec.pop("attempts_total")

    # ---- foundations ----
    topics = {"learned": [], "in_progress": [], "not_started": [], "gates_open": {}}
    if os.path.exists(FOUNDATIONS):
        with open(FOUNDATIONS) as f:
            fdefs = json.load(f)["topics"]
        seen = {}
        for path in sorted(glob.glob(os.path.join(TOPICS_DIR, "*.md"))):
            fm = parse_frontmatter(path)
            if fm and fm.get("topic"):
                seen[fm["topic"]] = fm.get("status") or "not-started"
        for t in fdefs:
            st = seen.get(t["id"], "not-started")
            key = {"learned": "learned", "in-progress": "in_progress"}.get(st, "not_started")
            topics[key].append(t["id"])
            if st != "learned":
                for g in t.get("gates_patterns", []):
                    topics["gates_open"].setdefault(g, []).append(t["id"])
    topics["blocks_everything"] = topics["gates_open"].get("*", [])

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
        "foundations": topics,
        "by_difficulty": by_difficulty,
        "companies_solved": dict(sorted(companies_solved.items(),
                                        key=lambda kv: -kv[1])),
        "oa": read_oa(),
        "position": {
            "solved": total_solved,
            "floor": READINESS["floor"],
            "interview_ready": READINESS["interview"],
            "strong": READINESS["strong"],
            "pct_to_floor": min(100, round(total_solved / READINESS["floor"] * 100)),
            "pct_to_interview": min(100, round(
                total_solved / READINESS["interview"] * 100)),
            "note": "A count is position, not readiness. Pair it with the bands: "
                    "180 solved at hint rung 5 is worse than 120 solved cold.",
        },
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
    print(f"difficulty: " + " · ".join(f"{k} {v}" for k, v in by_difficulty.items()))
    oa = read_oa()
    if oa:
        print(f"OA: {oa['attempts']} attempts over {oa['problems_attempted']} problems · "
              f"compiled first try {int(oa['compile_first_try_rate']*100)}%")
    print(f"due for revisit: {len(due)}")
    print(f"foundations: {len(topics['learned'])} learned, "
          f"{len(topics['in_progress'])} in progress, {len(topics['not_started'])} not started"
          + ("  ! blocks ALL patterns: " + ", ".join(topics["blocks_everything"])
             if topics["blocks_everything"] else ""))
    print(f"parsed {parsed} question files -> {STATS}")
    if unknown_pattern:
        print(f"! files with an unknown pattern id: {unknown_pattern}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
