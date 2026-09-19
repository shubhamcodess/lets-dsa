#!/usr/bin/env python3
"""
confusion.py — build a personal error profile from the learner's own history.

Every other DSA tool tells you what most people get wrong. This tells you what YOU get
wrong, because it reads data only your own sessions could have produced:

  * `## Defects Found` tables    the defect classes your pseudocode actually contains
  * `s1_wrong_guesses`           patterns you named before naming the right one
  * hints per pattern            where you needed the most help
  * lapses                       what you solved and then forgot

That last-but-one is the interesting one. If you repeatedly call sliding-window problems
"two pointers", that is a specific, fixable confusion — and no curriculum built for a
general audience can know it about you.

Writes state/confusion.json. Read-only over questions/.
"""

import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS = os.path.join(ROOT, "questions")
OUT = os.path.join(ROOT, "state", "confusion.json")
PATTERNS = os.path.join(ROOT, "config", "patterns.json")

DEFECT_CLASSES = {"OFF-BY-ONE", "UNHANDLED-EMPTY", "INVARIANT-BROKEN", "WRONG-COMPLEXITY",
                  "UNREACHABLE", "MUTATES-WHILE-ITERATING", "MISSING-UPDATE", "TYPE-MISMATCH"}

# What each defect class says about the underlying gap, and what to do about it.
DEFECT_MEANING = {
    "OFF-BY-ONE": ("Boundary reasoning. You are not tracing the ends.",
                   "Before coding, state what the first and last valid index ARE, out loud."),
    "UNHANDLED-EMPTY": ("You design for the typical case and bolt on edges after.",
                        "Make the empty/single-element case the FIRST thing your approach handles."),
    "INVARIANT-BROKEN": ("The invariant is not actually held in your head — it is decoration.",
                         "At S2, do not advance until you can say what breaks if it is violated."),
    "WRONG-COMPLEXITY": ("You are not counting operations, you are pattern-matching a label.",
                         "For every loop, say aloud how many times it runs at the constraint limit."),
    "UNREACHABLE": ("Control flow you have not traced.",
                    "Walk the branches on a concrete input before writing more."),
    "MUTATES-WHILE-ITERATING": ("Aliasing and in-place mutation.",
                                "Say explicitly which structure you are reading and which you are writing."),
    "MISSING-UPDATE": ("You define state but forget to maintain it.",
                       "List every variable, then for each say where it is updated."),
    "TYPE-MISMATCH": ("Sloppy about what a variable holds.",
                      "Name the type of every variable when you introduce it."),
}


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            fm[k.strip()] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
            continue
        v = v.strip('"').strip("'")
        if v in ("null", "", "~"):
            fm[k.strip()] = None
        else:
            try:
                fm[k.strip()] = int(v)
            except ValueError:
                fm[k.strip()] = v
    return fm


def main():
    pats = {p["id"]: p["name"] for p in json.load(open(PATTERNS))["patterns"]}
    defects = Counter()
    defect_where = defaultdict(list)
    confusions = Counter()
    hints_by_pattern = defaultdict(list)
    lapses = Counter()
    files = 0

    for path in sorted(glob.glob(os.path.join(QUESTIONS, "*", "*.md"))):
        text = open(path).read()
        fm = parse_frontmatter(text)
        if not fm.get("problem"):
            continue
        files += 1
        pid = fm.get("pattern")
        slug = fm.get("problem")

        # defect classes from the "## Defects Found" table
        sec = re.search(r"## Defects Found(.*?)(?=\n## |\Z)", text, re.S)
        if sec:
            for cell in re.findall(r"\|[^|\n]*\|\s*([A-Z][A-Z\-]+)\s*\|", sec.group(1)):
                if cell in DEFECT_CLASSES:
                    defects[cell] += 1
                    defect_where[cell].append(slug)

        # patterns they named before the right one
        for wrong in (fm.get("s1_wrong_guesses") or []):
            if wrong in pats and wrong != pid:
                confusions[(pid, wrong)] += 1

        if fm.get("status") == "solved" and pid:
            hints_by_pattern[pid].append(fm.get("hints_used") or 0)
            if fm.get("srs_lapses"):
                lapses[pid] += int(fm["srs_lapses"])

    top_defects = []
    for cls, n in defects.most_common():
        why, fix = DEFECT_MEANING.get(cls, ("", ""))
        top_defects.append({"class": cls, "count": n, "means": why, "drill": fix,
                            "seen_in": defect_where[cls][:5]})

    pairs = []
    for (right, wrong), n in confusions.most_common():
        pairs.append({"you_called_it": wrong, "it_was": right, "times": n,
                      "wrong_name": pats.get(wrong, wrong), "right_name": pats.get(right, right)})

    weak = []
    for pid, hs in hints_by_pattern.items():
        if hs:
            weak.append({"pattern": pid, "name": pats[pid], "solved": len(hs),
                         "avg_hints": round(sum(hs) / len(hs), 2), "lapses": lapses.get(pid, 0)})
    weak.sort(key=lambda r: (-r["avg_hints"], -r["lapses"]))

    out = {
        "schema": 1,
        "generated": date.today().isoformat(),
        "questions_scanned": files,
        "what_this_is":
            "A personal error profile, built only from this learner's own recorded sessions. "
            "Empty until they have solved problems and had defects recorded at S4. It is not "
            "a general list of common mistakes -- those are in config/patterns.json.",
        "defect_signature": top_defects,
        "pattern_confusions": pairs,
        "weakest_by_hints": weak[:8],
        "drill_recommendation": (
            f"Your most frequent defect is {top_defects[0]['class']} "
            f"({top_defects[0]['count']}x). {top_defects[0]['drill']}"
            if top_defects else
            "Not enough history yet. This fills in as defects are recorded at S4."),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"scanned {files} question files -> {OUT}")
    print(f"  defect classes seen : {len(top_defects)}")
    print(f"  pattern confusions  : {len(pairs)}")
    print(f"  patterns with data  : {len(weak)}")
    if top_defects:
        print(f"  top defect          : {top_defects[0]['class']} x{top_defects[0]['count']}")
    if pairs:
        p = pairs[0]
        print(f"  top confusion       : called it {p['wrong_name']}, was {p['right_name']} "
              f"({p['times']}x)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
