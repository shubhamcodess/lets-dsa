#!/usr/bin/env python3
"""
augment-briefs.py — add sub-pattern recognition signals to patterns/<id>.md.

RisingBrain names 91 sub-patterns, each with an `identification` line: what to look for in
a problem STATEMENT. Recognition is the skill this whole project claims to build, so that
text is the most valuable thing any of the seven sheets carries.

Sub-patterns are added INSIDE the existing 20 briefs, never alongside them. "DP on Stocks"
is a finer cut of 1-D DP, not a new family, and promoting it to a top-level pattern would
wreck the dependency tiers and the ladder for no gain.

Filler is dropped rather than printed: some entries carry marketing text ("frequently asked
in top tech companies") instead of a signal, and a brief padded with that is worse than one
without it.
"""

import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "curriculum", "sources", "risingbrain.raw.html")
EXTRA = os.path.join(ROOT, "config", "subpatterns-extra.json")

# An "identification" that says this rather than describing a problem is marketing.
FILLER = re.compile(r"frequently asked|top tech companies|high-frequency|must[- ]do|"
                    r"curated|interview questions$|master these", re.I)


def main():
    if not os.path.exists(SRC):
        print(f"! {SRC} missing — run build-curriculum.py --refresh first")
        return 1
    spec = importlib.util.spec_from_file_location(
        "bc", os.path.join(ROOT, "scripts", "build-curriculum.py"))
    bc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bc)

    rows = bc.parse_risingbrain(open(SRC, encoding="utf-8", errors="replace").read())
    by_pattern, dropped = {}, 0
    unmapped, noise = {}, {}
    for r in rows:
        sp, ident, strat = r.get("_subpattern"), r.get("_identification"), r.get("_strategy")
        if not sp or not ident:
            continue
        if FILLER.search(ident):
            dropped += 1
            continue
        pid = bc.rb_pattern_for(sp)
        if not pid:
            # An unmapped sub-pattern used to vanish here without a word. That is how
            # Kadane's Algorithm -- 5 problems, a named algorithm -- stayed out of every
            # brief. Split deliberate noise from a real gap, and report both.
            bucket = (noise if bc.rb_norm(sp) in {bc.rb_norm(n) for n in bc.RB_SUBPATTERN_NOISE}
                      else unmapped)
            bucket[sp] = bucket.get(sp, 0) + 1
            continue
        # Fold spelling variants ("Kadane's" vs "Kadane\u2019s", "Top-K" vs "Top K") onto one
        # row. Without this the same sub-pattern appeared twice in a brief.
        by_pattern.setdefault(pid, {}).setdefault(bc.rb_norm(sp), (sp, ident, strat))

    # Curated additions: techniques interviewers ask for that no sheet happens to name.
    extra_n = 0
    if os.path.exists(EXTRA):
        for pid, items in json.load(open(EXTRA)).items():
            if pid.startswith("_"):
                continue
            for it in items:
                by_pattern.setdefault(pid, {}).setdefault(
                    bc.rb_norm(it["name"]), (it["name"], it["recognize"], it["strategy"]))
                extra_n += 1

    written = 0
    for pid, subs in sorted(by_pattern.items()):
        path = os.path.join(ROOT, "patterns", f"{pid}.md")
        if not os.path.exists(path):
            print(f"  ! no brief for {pid}")
            continue
        text = open(path).read()

        block = ["## Sub-patterns inside this family\n",
                 "Finer cuts of the same idea. The **recognize** column is what to look for in a\n"
                 "problem statement — that is the transferable part.\n",
                 "| Sub-pattern | Recognize it when | What you do |",
                 "|---|---|---|"]
        for _key, (sp, ident, strat) in sorted(subs.items()):
            i = ident.rstrip(".").replace("|", "/")
            s = (strat or "").rstrip(".").replace("|", "/")
            block.append(f"| **{sp}** | {i} | {s} |")
        block.append("")
        new = "\n".join(block)

        if "## Sub-patterns inside this family" in text:
            text = re.sub(r"## Sub-patterns inside this family.*?(?=\n## )", new, text, flags=re.S)
        else:
            anchor = "## The invariant"
            if anchor not in text:
                anchor = "## The shape"
            if anchor not in text:
                print(f"  ! {pid}: no anchor, skipped")
                continue
            text = text.replace(anchor, new + "\n" + anchor, 1)
        open(path, "w").write(text)
        written += 1
        print(f"  {pid:24s} +{len(subs)} sub-patterns")

    print(f"\n  briefs updated : {written}")
    print(f"  curated added  : {extra_n} from config/subpatterns-extra.json")
    print(f"  filler dropped : {dropped} entries with marketing text instead of a signal")
    if noise:
        print(f"  noise dropped  : {sum(noise.values())} topic-level labels "
              f"({', '.join(sorted(noise))})")
    if unmapped:
        print(f"\n  ! UNMAPPED -- {sum(unmapped.values())} problems missing from the briefs.")
        print(f"  ! Add these to RB_SUBPATTERN_TO_PATTERN (or RB_SUBPATTERN_NOISE) "
              f"in build-curriculum.py:")
        for sp, n in sorted(unmapped.items(), key=lambda kv: -kv[1]):
            print(f"  !   {n:3d}  {sp}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
