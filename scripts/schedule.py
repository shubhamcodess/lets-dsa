#!/usr/bin/env python3
"""
schedule.py — spaced repetition for solved problems.

Replaces the old fixed intervals (+21 / +10 / +5 days), which ignored everything about
how the solve actually went and re-showed easy problems as often as hard ones.

This is an FSRS-INSPIRED scheduler, not FSRS-5. Real FSRS fits 17 parameters to a user's
own review history; there is no review history yet, so this uses published defaults and a
reduced 2-variable state (stability, difficulty). It is honest about that rather than
claiming an optimality it has not earned. Once ~100 reviews exist the parameters could be
fitted for real -- see `fit` below, which is deliberately not implemented yet.

The model:
  stability  S  how many days until recall probability falls to ~90%
  difficulty D  1-10, intrinsic hardness of this problem FOR THIS LEARNER
  grade         derived from hints used, attempts, and whether they downgraded --
                never self-reported, because "that was easy" is not evidence

Usage:
    python3 scripts/schedule.py grade --hints 2 --attempts 3
    python3 scripts/schedule.py next --grade good --stability 4.5 --difficulty 5.2
    python3 scripts/schedule.py due
"""

import argparse
import glob
import json
import math
import os
import sys
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS = os.path.join(ROOT, "questions")

# Initial stability in days, by grade. FSRS-style defaults, deliberately conservative:
# a clean solve earns a long gap, a struggle earns a short one.
S0 = {"again": 1.0, "hard": 2.5, "good": 5.0, "easy": 10.0}
D0 = {"again": 7.5, "hard": 6.0, "good": 5.0, "easy": 3.5}
GRADES = ("again", "hard", "good", "easy")
TARGET_RETENTION = 0.90
MAX_INTERVAL = 180


def grade_from(hints=0, attempts=1, downgraded=False, revisit_failed=False):
    """Derive the grade from what actually happened. Never from self-report.

    A learner who needed the invariant handed to them (rung 4+) has not demonstrated
    recall, whatever the submission says.
    """
    hints = hints or 0
    attempts = attempts or 1
    if downgraded or revisit_failed or hints >= 5:
        return "again"
    if hints >= 3 or attempts >= 4:
        return "hard"
    if hints >= 1 or attempts >= 2:
        return "good"
    return "easy"


def next_state(grade, stability=None, difficulty=None, reps=0, lapses=0):
    """One review -> new (stability, difficulty, interval_days, reps, lapses)."""
    if grade not in GRADES:
        raise ValueError(f"grade must be one of {GRADES}")

    first = stability is None or difficulty is None
    if first:
        S, D = S0[grade], D0[grade]
        reps, lapses = 1, (1 if grade == "again" else 0)
    else:
        S, D = float(stability), float(difficulty)
        reps += 1
        # Difficulty drifts toward the grade's anchor; it never resets.
        D = D + {"again": 1.2, "hard": 0.5, "good": -0.1, "easy": -0.6}[grade]
        D = min(10.0, max(1.0, D))
        if grade == "again":
            lapses += 1
            # A lapse must bring the problem back within DAYS. You failed to recall it;
            # scheduling it weeks out repeats the failure. Prior stability is credited
            # only weakly (you did know it once), and the result is capped at a week.
            S = max(1.0, min(S * 0.2, 7.0))
        else:
            # Easier problems and lower difficulty grow stability faster.
            gain = {"hard": 1.15, "good": 1.7, "easy": 2.4}[grade]
            damp = 1.0 - (D - 1.0) / 18.0          # D=10 -> ~0.5x growth
            S = S * (1.0 + (gain - 1.0) * damp)

    interval = S * math.log(TARGET_RETENTION) / math.log(0.9)
    interval = max(1, min(MAX_INTERVAL, round(interval)))
    return {"stability": round(S, 2), "difficulty": round(D, 2),
            "interval_days": interval, "reps": reps, "lapses": lapses,
            "due": (date.today() + timedelta(days=interval)).isoformat()}


def parse_frontmatter(path):
    try:
        text = open(path).read()
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
        else:
            try:
                fm[k.strip()] = int(v)
            except ValueError:
                try:
                    fm[k.strip()] = float(v)
                except ValueError:
                    fm[k.strip()] = v
    return fm


def cmd_grade(a):
    g = grade_from(a.hints, a.attempts, a.downgraded, a.revisit_failed)
    print(g)
    st = next_state(g)
    print(f"  first review -> stability {st['stability']}d, difficulty {st['difficulty']}, "
          f"due in {st['interval_days']}d ({st['due']})")
    return 0


def cmd_next(a):
    st = next_state(a.grade, a.stability, a.difficulty, a.reps, a.lapses)
    print(json.dumps(st, indent=1))
    return 0


def cmd_due(a):
    today = date.today().isoformat()
    due, upcoming = [], []
    for path in sorted(glob.glob(os.path.join(QUESTIONS, "*", "*.md"))):
        fm = parse_frontmatter(path)
        if not fm or fm.get("status") != "solved":
            continue
        d = fm.get("srs_due") or fm.get("revisit_on")
        if not d:
            continue
        rec = {"problem": fm.get("problem"), "pattern": fm.get("pattern"), "due": d,
               "stability": fm.get("srs_stability"), "lapses": fm.get("srs_lapses", 0),
               "path": os.path.relpath(path, ROOT)}
        (due if str(d) <= today else upcoming).append(rec)
    due.sort(key=lambda r: r["due"])
    upcoming.sort(key=lambda r: r["due"])
    if a.json:
        print(json.dumps({"due": due, "upcoming": upcoming[:10]}, indent=1))
        return 0
    print(f"due now: {len(due)}")
    for r in due[:15]:
        print(f"  {r['due']}  {r['pattern']:22s} {r['problem']}"
              + (f"  (lapsed {r['lapses']}x)" if r["lapses"] else ""))
    if upcoming:
        print(f"\nnext up: {upcoming[0]['due']}  {upcoming[0]['problem']}")
    return 0


def cmd_fit(a):
    print("Not implemented, deliberately.")
    print("Real FSRS fits 17 parameters to YOUR review history. With fewer than ~100")
    print("reviews that fit is noise, and would be worse than the published defaults")
    print("this scheduler uses now. Revisit once the review log is large enough.")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    g = sub.add_parser("grade", help="derive a grade from what happened")
    g.add_argument("--hints", type=int, default=0)
    g.add_argument("--attempts", type=int, default=1)
    g.add_argument("--downgraded", action="store_true")
    g.add_argument("--revisit-failed", action="store_true")
    g.set_defaults(fn=cmd_grade)
    n = sub.add_parser("next", help="compute the next interval")
    n.add_argument("--grade", required=True, choices=GRADES)
    n.add_argument("--stability", type=float)
    n.add_argument("--difficulty", type=float)
    n.add_argument("--reps", type=int, default=0)
    n.add_argument("--lapses", type=int, default=0)
    n.set_defaults(fn=cmd_next)
    d = sub.add_parser("due", help="what is due for review")
    d.add_argument("--json", action="store_true")
    d.set_defaults(fn=cmd_due)
    sub.add_parser("fit").set_defaults(fn=cmd_fit)
    args = ap.parse_args()
    if not getattr(args, "fn", None):
        ap.print_help()
        return 0
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
