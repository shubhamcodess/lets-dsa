#!/usr/bin/env python3
"""
build-track.py — materialize the learning ladder into curriculum/track.md.

Answers, as a file you can read rather than a rule buried in a skill:
  which pattern first, why that one, how many problems before moving on,
  which problems specifically, and in what order.

Three independent orderings compose here:

1. BETWEEN patterns — the dependency graph in config/patterns.json (`depends_on`).
   Topologically sorted into tiers. A pattern never appears before its prerequisites.

2. WITHIN a pattern — difficulty ramp first, consensus second.
   Easy -> Medium -> Hard, and inside each difficulty band the problem sitting in the
   most curated sheets comes first. Appearing in 5 of 7 sheets means five independent
   curators spent scarce attention on it; appearing in one is that curator's taste.

3. ADVANCEMENT — explicit exit criteria per tier (below). Foundational patterns demand
   more problems because everything later leans on them; late patterns demand fewer
   because by then the learner transfers rather than starts cold.

Nothing here is a model or a score. It is a stated, auditable rule you can disagree with.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGED = os.path.join(ROOT, "curriculum", "merged.json")
PATTERNS = os.path.join(ROOT, "config", "patterns.json")
FOUNDATIONS = os.path.join(ROOT, "config", "foundations.json")
OUT = os.path.join(ROOT, "curriculum", "track.md")

# tier -> (problems needed to advance, required difficulty mix, why)
TIER_RULES = {
    1: (6, {"Easy": 2, "Medium": 3}, "Everything downstream leans on this. Over-invest here."),
    2: (5, {"Easy": 1, "Medium": 3}, "Core interview surface. Needs real depth."),
    3: (5, {"Easy": 1, "Medium": 3}, "Where most interviews actually live."),
    4: (4, {"Medium": 3}, "You are transferring now, not starting cold."),
    5: (4, {"Medium": 3}, "Expensive patterns. Depth over breadth."),
    6: (3, {"Medium": 2}, "Late and narrow. Enough to recognize and adapt."),
}

DIFF_ORDER = {"Easy": 0, "Medium": 1, "Hard": 2}

# Three readiness levels, not one number. The floor tells you when you may MOVE ON from a
# pattern; it does not tell you when you are ready to interview. Conflating the two is how
# someone finishes a tracker and fails a loop.
READINESS = {
    "floor":       (None, "Covered the map. You can recognize every pattern. Not interview-ready."),
    "interview":   (180,  "Realistic target for product-based interviews. Weighted toward the "
                          "patterns interviewers actually reach for."),
    "strong":      (250,  "Depth in the high-frequency patterns, plus the Hard tier where it "
                          "matters. Comfortable rather than surviving."),
}


def allocate(budget, floors, weights, avail):
    """Split `budget` across patterns proportional to interview frequency, never below a
    pattern's floor and never above what exists. Clamping redistributes, so iterate."""
    ids = list(floors)
    out = {k: floors[k] for k in ids}
    remaining = budget - sum(out.values())
    for _ in range(50):
        if remaining <= 0:
            break
        open_ids = [k for k in ids if out[k] < avail[k]]
        if not open_ids:
            break
        tw = sum(weights[k] for k in open_ids) or 1
        added = 0
        for k in open_ids:
            share = weights[k] / tw
            give = max(1, round(remaining * share)) if remaining > 0 else 0
            give = min(give, avail[k] - out[k], remaining - added)
            out[k] += give
            added += give
            if added >= remaining:
                break
        if added == 0:
            break
        remaining -= added
    return out


def tiers(patterns):
    """Topologically sort patterns into dependency tiers."""
    dep = {p["id"]: list(p.get("depends_on", [])) for p in patterns}
    placed, out, tier = set(), [], 1
    while len(placed) < len(dep):
        wave = sorted(p for p, d in dep.items() if p not in placed and all(x in placed for x in d))
        if not wave:
            raise SystemExit(f"! dependency cycle among {sorted(set(dep) - placed)}")
        out.append((tier, wave))
        placed |= set(wave)
        tier += 1
    return out


def main():
    merged = json.load(open(MERGED))
    pats = json.load(open(PATTERNS))["patterns"]
    pmeta = {p["id"]: p for p in pats}
    founds = json.load(open(FOUNDATIONS))["topics"] if os.path.exists(FOUNDATIONS) else []

    gates = {}
    for t in founds:
        for g in t.get("gates_patterns", []):
            gates.setdefault(g, []).append(t)

    by_pattern = {}
    for p in merged["problems"].values():
        by_pattern.setdefault(p["pattern"], []).append(p)

    def rank(p):
        # difficulty first, then consensus (more sheets = earlier), then id for stability
        return (DIFF_ORDER.get(p["difficulty"], 3), -len(p["lists"]), p["leetcode_id"] or 0)

    L = []
    w = L.append
    w("# Your Learning Track\n")
    w(f"_Generated by `scripts/build-track.py` from {merged['counts']['total']} verified "
      f"problems · {merged['built']}_\n")
    w("This is the ladder. Patterns are ordered so a pattern never appears before the ones it\n"
      "depends on. Inside a pattern, problems run Easy → Medium → Hard, and within a difficulty\n"
      "the problem in the most curated sheets comes first.\n")
    w("**How to read `sheets`:** how many of the 7 curated lists contain that problem. 5+ means\n"
      "five independent curators picked it. 1 means one did.\n")

    always = [t for t in founds if "*" in t.get("gates_patterns", [])]
    if always:
        w("\n---\n\n## Before anything — required foundations\n")
        for t in always:
            w(f"- [ ] **{t['name']}** (`{t['id']}`) — {t['est_minutes']} min. "
              f"Gates **every pattern**.")
            w(f"      {t['why_first'].splitlines()[0]}")
    w("")

    total_needed = 0
    for tier, ids in tiers(pats):
        need, mix, why = TIER_RULES.get(tier, (3, {"Medium": 2}, ""))
        mixs = " + ".join(f"{v} {k}" for k, v in mix.items())
        w(f"\n---\n\n# Tier {tier}\n")
        w(f"**Advance after {need} problems per pattern** ({mixs} minimum). _{why}_\n")

        for pid in ids:
            meta = pmeta[pid]
            probs = sorted(by_pattern.get(pid, []), key=rank)
            total_needed += min(need, len(probs))
            deps = meta.get("depends_on") or []
            w(f"\n## {meta['name']}  `{pid}`\n")
            w(f"> {meta['core_idea']}\n")
            if deps:
                w(f"_Requires first: {', '.join(deps)}_")
            for t in gates.get(pid, []):
                w(f"_Foundation gate: **{t['name']}** ({t['est_minutes']} min) — "
                  f"cover before the first problem here._")
            avail = len(probs)
            w(f"_Available: {avail} · solve {min(need, avail)} to advance_\n")
            # Show enough of EACH difficulty to actually satisfy the stated mix,
            # plus a small buffer. A flat top-N slice returns all Easy and makes the
            # "2 Easy + 3 Medium" rule unsatisfiable from the list shown.
            shown, buckets = [], {}
            for pr in probs:
                buckets.setdefault(pr["difficulty"], []).append(pr)
            for diff in ("Easy", "Medium", "Hard"):
                quota = mix.get(diff, 0)
                take = quota + 2 if quota else (2 if diff == "Hard" else 0)
                shown += buckets.get(diff, [])[:take]
            shown.sort(key=rank)
            w("| ✓ | Problem | Difficulty | Sheets | Link |")
            w("|---|---|---|---|---|")
            for pr in shown:
                paid = " 🔒" if pr.get("paid_only") else ""
                w(f"| [ ] | {pr['title']}{paid} | {pr['difficulty']} | {len(pr['lists'])} | "
                  f"[#{pr['leetcode_id']}](https://leetcode.com/problems/{pr['slug']}/) |")
            if avail > len(shown):
                w(f"\n_+{avail - len(shown)} more in this pattern once these are done._")

    # ---- readiness targets ----
    floors, weights, avail_n = {}, {}, {}
    for tier, ids in tiers(pats):
        need = TIER_RULES.get(tier, (3,))[0]
        for pid in ids:
            n = len(by_pattern.get(pid, []))
            floors[pid] = min(need, n)
            weights[pid] = sum(len(p["lists"]) for p in by_pattern.get(pid, []))
            avail_n[pid] = n
    interview = allocate(READINESS["interview"][0], floors, weights, avail_n)
    strong = allocate(READINESS["strong"][0], floors, weights, avail_n)

    w("\n---\n\n## Readiness targets — three levels, not one number\n")
    w("The floor tells you when you may **move on** from a pattern. It does not tell you when\n"
      "you are ready to **interview**. Those are different questions, and conflating them is how\n"
      "someone finishes a tracker and then fails a loop.\n")
    w(f"| Level | Problems | What it means |")
    w("|---|---|---|")
    w(f"| **Floor** | {sum(floors.values())} | {READINESS['floor'][1]} |")
    w(f"| **Interview-ready** | {sum(interview.values())} | {READINESS['interview'][1]} |")
    w(f"| **Strong** | {sum(strong.values())} | {READINESS['strong'][1]} |")
    w("\nBeyond the floor, problems are allocated by **interview frequency** — measured as how\n"
      "much weight the seven curated sheets put on each pattern, not by my opinion. Trees carries\n"
      "15% of all sheet weight; fast-slow pointers carries 1%. Spreading effort evenly across\n"
      "20 patterns would be the wrong shape.\n")
    w("| Pattern | Available | Floor | Interview-ready | Strong | Share of sheet weight |")
    w("|---|---|---|---|---|---|")
    tw = sum(weights.values()) or 1
    for pid in sorted(weights, key=lambda x: -weights[x]):
        w(f"| {pmeta[pid]['name']} | {avail_n[pid]} | {floors[pid]} | {interview[pid]} | "
          f"{strong[pid]} | {weights[pid]/tw*100:.1f}% |")
    w("\n**None of these numbers is mastery on its own.** 180 solved at hint rung 5 is worse than\n"
      "120 solved cold. `progress-report` bands each pattern on your real hint and attempt counts,\n"
      "and a pattern only reaches `solid` after a revisit you passed without help.\n")

    w("\n---\n\n## Exit criteria — when a pattern is genuinely done\n")
    w("Solving the count above is the floor, not the proof. A pattern counts as held when:\n")
    w("| Band | Means |")
    w("|---|---|")
    w("| `solid` | ≥3 solved, ≤1 average hints, **and** one cold revisit passed |")
    w("| `working` | ≥2 solved, ≤3 average hints |")
    w("| `exposed` | solved only with heavy hints — not mastery |")
    w("\n`progress-report` computes these from your real hint and attempt counts. "
      "A problem solved at rung 5 after four attempts is exposure, not mastery, and the "
      "report says so rather than counting it.\n")
    w(f"\n_Floor across the ladder: **{total_needed} problems**. "
      f"Interview-ready: **{sum(interview.values())}**. Strong: **{sum(strong.values())}**._")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write("\n".join(L) + "\n")

    print(f"Wrote {OUT}")
    for tier, ids in tiers(pats):
        need = TIER_RULES.get(tier, (3,))[0]
        print(f"  tier {tier}: {len(ids)} patterns, {need} problems each -> "
              f"{', '.join(i.split('-',1)[1] for i in ids)}")
    print(f"  floor across the whole ladder: {total_needed} problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
