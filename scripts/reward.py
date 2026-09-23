#!/usr/bin/env python3
"""
reward.py -- the after-solve card. Read-only presentation, run at S6 AFTER roll-stats.py.

Design decisions worth not re-litigating later:

  * The headline is EARNED or absent. A card that fires identically after a clean solve
    and after a five-hint grind stops meaning anything by week two, and trains the
    learner to skim past it.

  * It never leads with the count. Leading with "12 / 90" pays them to farm hints and
    rush, which is the exact failure this whole framework exists to prevent. The
    readiness bar is deliberately the SECOND thing on the card.

  * No daily streaks. A streak rewards attendance and punishes a missed day, which
    produces streak-protection behaviour rather than learning. The streak here is
    consecutive HINT-FREE solves -- performance, not turning up.

  * No generic motivational quotes. A rotating quote is wallpaper by problem five and is
    the extrinsic reward that erodes intrinsic motivation. The slot holds a fact from
    THEIR OWN history instead, which is the one thing nothing else in their life can
    produce: "two-pointers took you 4 hints in August; this one took 0".

  * Every number here comes from questions/**/*.md and state/stats.json. LeetCode auth is
    off, so their real LeetCode profile is unreadable -- anything claiming to be a
    LeetCode stat would be our own count wearing LeetCode's clothes. The card says
    "recorded here" and means it.

Writes nothing. roll-stats.py owns stats.json; record-solve owns the question file.

Usage:
    python3 scripts/reward.py --solved <slug>     # markdown card (the default)
    python3 scripts/reward.py --solved <slug> --json   # + widget payload on a milestone
"""

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS = os.path.join(ROOT, "questions")
STATS = os.path.join(ROOT, "state", "stats.json")
PATTERNS = os.path.join(ROOT, "config", "patterns.json")

# Same three numbers build-track.py publishes. A count is position, never mastery.
TARGETS = [(90, "floor"), (180, "interview-ready"), (250, "strong")]
BAND_RANK = {"untouched": 0, "exposed": 1, "working": 2, "solid": 3}
MILESTONE_EVERY = 10


def parse_frontmatter(path):
    """Flat-scalar YAML frontmatter, same shape roll-stats.py writes and reads."""
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
        k = k.strip()
        if v in ("null", "", "~"):
            fm[k] = None
        elif v.lower() in ("true", "false"):
            fm[k] = v.lower() == "true"
        elif v.lstrip("-").isdigit():
            fm[k] = int(v)
        else:
            fm[k] = v
    return fm


def band(solved, avg_hints, revisit_passed):
    """Mirrors roll-stats.py exactly. If that changes, change this."""
    if solved == 0:
        return "untouched"
    if solved >= 3 and avg_hints is not None and avg_hints <= 1.0 and revisit_passed:
        return "solid"
    if solved >= 2 and avg_hints is not None and avg_hints <= 3.0:
        return "working"
    return "exposed"


def load_solves():
    out = []
    for p in sorted(glob.glob(os.path.join(QUESTIONS, "*", "*.md"))):
        fm = parse_frontmatter(p)
        if not fm or fm.get("status") != "solved":
            continue
        fm["_slug"] = fm.get("problem") or os.path.basename(p)[:-3]
        fm["_hints"] = fm.get("hints_used") or 0
        out.append(fm)
    out.sort(key=lambda f: (f.get("solved_on") or "", f["_slug"]))
    return out


def band_for(rows, revisit_passed):
    n = len(rows)
    if not n:
        return "untouched"
    avg = sum(r["_hints"] for r in rows) / n
    return band(n, avg, revisit_passed)


def headline(this, solves, stats):
    """Return (text, is_milestone) or (None, False).

    Ordered by how hard the thing was to earn. First match wins, and a grind earns
    nothing -- that silence is the point.
    """
    pat = this.get("pattern")
    hints = this["_hints"]
    # Position of THIS solve in the chronological run -- not the count on disk. Using
    # len(solves) made the card depend on when it ran rather than on what was solved, so
    # re-running it for an older problem produced a headline about a later one.
    idx = next(i for i, s in enumerate(solves) if s["_slug"] == this["_slug"])
    prior = solves[:idx]
    total = idx + 1
    same = [s for s in prior if s.get("pattern") == pat]

    pname = {}
    try:
        pname = {p["id"]: p["name"] for p in json.load(open(PATTERNS))["patterns"]}
    except Exception:
        pass
    label = pname.get(pat, pat)

    # -- milestones: the three things that unlock a widget -----------------------
    revisit = False
    for row in stats.get("patterns", []):
        if row.get("pattern") == pat:
            revisit = bool(row.get("revisit_passed"))
            break
    before = band_for(same, revisit)
    after = band_for(same + [this], revisit)
    # untouched -> exposed is not an achievement, it is showing up once. Treating it as
    # a milestone would fire a widget on the first problem of all 20 patterns -- an
    # attendance reward, which is the thing this card is built to avoid. It still earns a
    # headline below ("First problem in X"), just not a celebration.
    if BAND_RANK[after] > BAND_RANK[before] and BAND_RANK[before] >= 1:
        return (f"**{label} moved {before} → {after}.** "
                f"{len(same) + 1} solved in this pattern, "
                f"{sum(s['_hints'] for s in same + [this]) / (len(same) + 1):.1f} hints average.",
                True)

    for n, name in TARGETS:
        if len(prior) < n <= total:
            return (f"**You crossed {n} — {name}.** "
                    f"That is position on the map, not mastery; the bands say the rest.", True)

    if total % MILESTONE_EVERY == 0:
        clean = sum(1 for s in prior + [this] if s["_hints"] == 0)
        return (f"**{total} solved.** {clean} of them with no hints at all.", True)

    # -- earned, but not milestone-worthy ---------------------------------------
    if hints >= 3:
        return (None, False)          # deliberately silent. A grind is not a win.

    if hints == 0:
        streak = 0
        for s in reversed(prior + [this]):
            if s["_hints"] == 0:
                streak += 1
            else:
                break
        if streak >= 3:
            return (f"**{streak} solves in a row with no hints.**", False)

        if same:
            avg = sum(s["_hints"] for s in same) / len(same)
            if avg >= 1.5:
                worst = max(same, key=lambda s: s["_hints"])
                return (f"**No hints.** {label} used to cost you "
                        f"{avg:.1f} on average — {worst.get('title', worst['_slug'])} "
                        f"took {worst['_hints']}.", False)

        diff = (this.get("difficulty") or "").lower()
        if diff in ("medium", "hard"):
            first = not any(s["_hints"] == 0 and (s.get("difficulty") or "").lower() == diff
                            for s in prior)
            if first:
                return (f"**First {diff.title()} solved with no hints.**", False)
        if not same:
            return (f"**First problem in {label} — and no hints.**", False)
        return ("**No hints.**", False)

    if this.get("s1_wrong_guesses") in (None, "[]", ""):
        if same and any(s.get("s1_wrong_guesses") not in (None, "[]", "") for s in same):
            return (f"**You named the pattern first try.** "
                    f"You have misread {label} before.", False)
    return (None, False)


def bar(n, width=22):
    """Progress toward the next target only. The full 250 as one bar reads as 'barely
    started' for months, which is discouraging and also just less informative."""
    target = next((t for t, _ in TARGETS if n < t), TARGETS[-1][0])
    filled = min(width, int(round(width * n / target)))
    return f"`{'█' * filled}{'·' * (width - filled)}` **{n}/{target}**"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solved", required=True, help="slug of the problem just recorded")
    ap.add_argument("--json", action="store_true", help="also emit the widget payload")
    a = ap.parse_args()

    if not os.path.exists(STATS):
        print("! state/stats.json missing — run scripts/roll-stats.py first", file=sys.stderr)
        return 1
    stats = json.load(open(STATS))
    solves = load_solves()
    this = next((s for s in solves if s["_slug"] == a.solved), None)
    if not this:
        print(f"! {a.solved} is not recorded as solved — run this after the file is written",
              file=sys.stderr)
        return 1

    total = next(i for i, s in enumerate(solves) if s["_slug"] == a.solved) + 1
    text, milestone = headline(this, solves, stats)
    nxt = next((t for t, _ in TARGETS if total < t), None)

    lines = []
    if text:
        lines.append(text)
    else:
        # No headline earned. Say what it cost instead -- plainly, without judgement.
        lines.append(f"Recorded: **{this.get('title', a.solved)}** · "
                     f"{this['_hints']} hint{'s' if this['_hints'] != 1 else ''} · "
                     f"{this.get('attempts', 1)} attempt"
                     f"{'s' if (this.get('attempts') or 1) != 1 else ''}.")
    lines.append("")
    lines.append(f"{bar(total)} recorded here"
                 + (f" · {nxt - total} to {dict(TARGETS)[nxt]}" if nxt else ""))

    b = stats.get("bands", {})
    lines.append(f"solid {b.get('solid', 0)} · working {b.get('working', 0)} · "
                 f"exposed {b.get('exposed', 0)} · untouched {b.get('untouched', 0)}"
                 f"  —  {stats.get('totals', {}).get('patterns_touched', 0)}/20 patterns met")

    print("\n".join(lines))

    if a.json:
        print("\n--- WIDGET ---" if milestone else "\n--- NO WIDGET ---")
        if milestone:
            print(json.dumps({
                "headline": text, "solved": total, "next_target": nxt,
                "bands": b, "pattern": this.get("pattern"),
                "hints": this["_hints"], "title": this.get("title"),
            }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
