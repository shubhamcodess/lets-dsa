#!/usr/bin/env python3
"""
build-foundations.py — build the "learn this before you solve anything" layer.

Foundations are topics, not problems. They are what a learner needs BEFORE the S0-S6
loop makes any sense: if you cannot reason about the cost of a loop, the S3 ladder gate
is unpassable, and if you have never traced a recursive call, S2 on a tree problem is
not a gate, it is a wall.

Topic groupings and their free article/video links come from Striver's A2Z steps 1-2
(already fetched into curriculum/merged.json). One topic -- complexity analysis -- is
authored rather than sourced, and is marked as such: A2Z folds it into "Things to Know",
but it gates every single problem in the system and deserves to be its own gate.

Writes config/foundations.json. Run after build-curriculum.py.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGED = os.path.join(ROOT, "curriculum", "merged.json")
OUT = os.path.join(ROOT, "config", "foundations.json")
PATTERNS = os.path.join(ROOT, "config", "patterns.json")

ALL = "*"

# id -> (name, A2Z substeps that supply its material, why it gates, patterns gated, minutes)
TOPICS = [
    ("00-language-basics", "Language Basics",
     ["Things to Know in C++/Java/Python or any language"],
     "You cannot express an algorithm you cannot type. Input/output, loops, functions "
     "and pass-by-reference are the vocabulary every later topic assumes.",
     [], 120),

    ("01-complexity-analysis", "Complexity Analysis",
     [],  # authored — see AUTHORED below
     "This gates everything. The S3 ladder asks for time and space on three approaches; "
     "without it that gate is unpassable and the learner cannot tell a good solution "
     "from a lucky one. It is also the single most common thing interviewers probe.",
     [ALL], 90),

    ("02-logical-thinking", "Loops & Pattern Printing",
     ["Patterns", "Build-up Logical Thinking"],
     "Nested-loop intuition. Knowing what the inner loop costs, and being able to hold "
     "two indices in your head at once, is the prerequisite for every two-pointer and "
     "matrix problem later.",
     [], 150),

    ("03-collections", "Arrays, Lists, Maps & Sets",
     ["Learn STL/Java-Collections or similar thing in your language"],
     "The containers you will reach for in every problem, and — more importantly — what "
     "each operation actually costs. Picking a list where a set was needed is the most "
     "common cause of an accidental O(n^2).",
     ["01-arrays-hashing"], 120),

    ("04-basic-maths", "Basic Maths",
     ["Know Basic Maths"],
     "Digit manipulation, primes, GCD, and where integer overflow bites. Small surface "
     "area, and it is the whole of two patterns.",
     ["19-bit-manipulation", "20-math-geometry"], 90),

    ("05-basic-recursion", "Recursion & the Call Stack",
     ["Learn Basic Recursion"],
     "The hinge of the whole curriculum. Trees, backtracking, graphs and DP are all "
     "recursion wearing different hats. A learner who has not traced a call stack by "
     "hand will fail the S2 dry run on every one of them.",
     ["09-trees", "12-backtracking", "13-graphs", "17-1d-dp", "18-2d-dp"], 180),

    ("06-basic-hashing", "Hashing & Frequency Counting",
     ["Learn Basic Hashing"],
     "Trading space for time is the first real optimization most learners meet, and the "
     "move that turns a nested scan into a single pass.",
     ["01-arrays-hashing", "03-sliding-window"], 90),

    ("07-sorting", "Sorting",
     ["Sorting-I", "Sorting-II"],
     "Less about implementing sorts than knowing that sorting costs n log n and what it "
     "buys: once data is ordered, two pointers, binary search and interval sweeps all "
     "become available.",
     ["02-two-pointers", "04-binary-search", "15-intervals", "16-greedy"], 150),
]

AUTHORED = {
    "01-complexity-analysis": {
        "covers": [
            "Counting operations: how many times does this line actually run?",
            "Big-O, and why constants and lower-order terms are dropped",
            "Reading constraints to infer the required complexity "
            "(n <= 10^5 rules out O(n^2))",
            "Space complexity, including the recursion stack",
            "Amortized cost: why a sliding window is O(n) despite two nested-looking pointers",
        ],
        "note": "Authored for this curriculum, not taken from a sheet. A2Z folds this "
                "into 'Things to Know'; it is split out because it gates every pattern "
                "and because the S3 ladder gate is built directly on it.",
    }
}


def main():
    if not os.path.exists(MERGED):
        print(f"! {MERGED} missing — run scripts/build-curriculum.py first")
        return 1
    with open(MERGED) as f:
        merged = json.load(f)
    valid = {p["id"] for p in json.load(open(PATTERNS))["patterns"]}

    # Substep labels arrive with embedded newlines and runs of spaces from the source
    # page's markup, so match on normalized whitespace rather than the literal string.
    def norm(x):
        return re.sub(r"\s+", " ", x).strip().lower() if isinstance(x, str) else ""

    # index A2Z steps 1-2 material by substep
    by_sub = {}
    for r in merged.get("non_leetcode", []):
        if r.get("list") == "striver_a2z" and r.get("step_no") in (1, 2):
            by_sub.setdefault(norm(r.get("substep")), []).append(r)
    # a handful of foundations items ARE on leetcode — pick those up too
    for p in merged.get("problems", {}).values():
        s = p.get("striver")
        if s and s.get("step_no") in (1, 2):
            by_sub.setdefault(norm(s.get("substep")), []).append({
                "name": p["title"], "article": p.get("resources", {}).get("article"),
                "youtube": p.get("resources", {}).get("youtube"),
                "leetcode": f"https://leetcode.com/problems/{p['slug']}/"})

    topics, unmatched = [], []
    for tid, name, subs, why, gates, mins in TOPICS:
        bad = [g for g in gates if g != ALL and g not in valid]
        if bad:
            print(f"! {tid} gates unknown pattern ids: {bad}")

        items, resources = [], []
        for sub in subs:
            rows = by_sub.get(norm(sub))
            if rows is None:
                unmatched.append((tid, sub))
                continue
            for r in rows:
                items.append(r.get("name"))
                if r.get("article") or r.get("youtube"):
                    resources.append({"for": r.get("name"), "article": r.get("article"),
                                      "youtube": r.get("youtube"),
                                      "leetcode": r.get("leetcode")})

        entry = {
            "id": tid, "name": name, "why_first": why,
            "gates_patterns": gates, "est_minutes": mins,
            "source": "striver_a2z steps 1-2" if subs else "authored",
            "source_substeps": subs,
            "exercise_count": len(items),
            "exercises": sorted(set(x for x in items if x)),
            "resources": resources,
        }
        if tid in AUTHORED:
            entry.update(AUTHORED[tid])
        topics.append(entry)

    out = {
        "schema": 1,
        "built": merged.get("built"),
        "what_this_is":
            "Topics to learn BEFORE attempting problems. The S0-S6 loop assumes these. "
            "A learner who cannot reason about loop cost cannot pass the S3 ladder gate, "
            "and one who has never traced a call stack cannot pass S2 on a tree problem. "
            "Skipping these is the most common reason a learner stalls at the first Medium.",
        "gating_rule":
            "A topic with gates_patterns ['*'] must be covered before ANY problem. "
            "Otherwise a pattern's gating topics should be covered before its first "
            "problem. daily-drill enforces this; it can be overridden on request, and "
            "the override is recorded so progress-report tells the truth later.",
        "counts": {
            "topics": len(topics),
            "total_minutes": sum(t["est_minutes"] for t in topics),
            "exercises": sum(t["exercise_count"] for t in topics),
            "resources": sum(len(t["resources"]) for t in topics),
        },
        "topics": topics,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"Wrote {OUT}")
    for t in topics:
        g = "ALL patterns" if ALL in t["gates_patterns"] else (
            f"{len(t['gates_patterns'])} patterns" if t["gates_patterns"] else "—")
        print(f"  {t['id']:24s} {t['est_minutes']:4d}m  {t['exercise_count']:3d} ex  "
              f"{len(t['resources']):3d} links  gates {g}")
    print(f"  total: {out['counts']['total_minutes']} min, "
          f"{out['counts']['exercises']} exercises, {out['counts']['resources']} free links")
    if unmatched:
        print("! substeps not found in merged.json (source page may have changed):")
        for tid, sub in unmatched:
            print(f"    {tid}: {sub!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
