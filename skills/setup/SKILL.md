---
name: setup
description: >
  First-run onboarding. Invoke on a fresh clone or when config/user.json is missing.
  Triggers on: "setup", "get started", "initialize", "first time", "configure", and
  automatically whenever the Setup Gate in CLAUDE.md fails. Six phases, each verified
  before the next. Writes config/user.json, builds the curriculum, generates the
  personal track, and creates the initial state files.
---

# Setup Skill

Six phases. **Verify each one before moving on, and say what actually worked** — not what you assume worked.

---

## Phase 1 — Check the environment

Run and report the real output:

```
python3 --version
git --version
git rev-parse --is-inside-work-tree 2>/dev/null || echo "not a git repo"
```

| Result | Do |
|---|---|
| Not a git repo | Offer `git init`. Every write in this system is committed; without git the progress record has no history. |
| No python3 | Stop. `scripts/build-curriculum.py` needs it. Tell them to install it. |
| All present | Continue. |

## Phase 2 — Verify the LeetCode MCP

Call `get_daily_challenge`. It takes no arguments and needs no auth.

| Result | Do |
|---|---|
| Returns a problem | Say which one. That is the proof it works. Continue. |
| Fails | Report the actual error. Check `mcp/.mcp.json` exists and the server name is `leetcode`. Do not continue pretending it works — S0 depends on `get_problem`. |

**Do not claim the MCP works because the config file exists.** Configuration is not connection.

## Phase 3 — Interview them

Ask these one at a time. Don't dump all five at once.

1. **Level.** "Where are you now — have you done much DSA, or is this near-scratch?" Map their answer to `beginner` / `intermediate` / `advanced`. If they're unsure, ask: "Given a sorted array and asked for two numbers summing to a target, what do you reach for?" No answer → beginner. "Two pointers" → intermediate. Mentions the tradeoff against hashing → advanced.
2. **Target companies.** Free text. Store as given.
3. **Timeline.** Weeks until they want to be interview-ready.
4. **Daily budget.** Problems per day, or minutes per day. Be realistic with them — 2 problems properly understood beats 6 skimmed.
5. **Language.** The one they'll submit in.

## Phase 4 — Write config/user.json

```json
{
  "schema": 1,
  "level": "intermediate",
  "language": "python",
  "target_companies": ["Google", "Atlassian", "Uber"],
  "timeline_weeks": 12,
  "daily_budget_problems": 2,
  "created": "2026-09-18"
}
```

Show it to them and confirm before writing. Commit `setup: config/user.json`.

## Phase 5 — Build the curriculum

```
python3 scripts/build-curriculum.py --verify
```

This takes 2–3 minutes — it verifies every slug against LeetCode's public GraphQL. Report the real numbers it prints: total, per-pattern counts, anything dropped.

| Result | Do |
|---|---|
| 150 verified, 0 dropped | Say so. Continue. |
| Some dropped | Name them. They're excluded from the track. That's correct behaviour, not a failure. |
| Network failure | Report it. Offer to run without `--verify` — the track still works, just without ids and tags. |

Then generate `curriculum/track.md` from `merged.json` + `user.json`:

- Pattern order follows `depends_on` in `config/patterns.json`. Never schedule a pattern before its dependency.
- Within a pattern: Easy → Medium → Hard, and **never jump a difficulty tier with fewer than 2 problems at the tier below**. That jump is the thing this whole system exists to prevent.
- Size it to `timeline_weeks × 7 × daily_budget_problems`. If the full 150 doesn't fit, cut by pattern *breadth* last and by *depth within a pattern* first — better to know 12 patterns at 3 problems each than 6 at 6.
- Flag the 7 paid-only problems. Substitute a free sibling from the same pattern if they don't have Premium.

## Phase 6 — Initialize state

Write `state/current.json`:

```json
{
  "schema": 1,
  "updated": "2026-09-18T00:00:00+05:30",
  "active": null,
  "parked": [],
  "counters": { "solved": 0, "downgrades": 0, "refusals_issued": 0 }
}
```

Write `state/current.md` with `Resume From: Nothing started yet. Offer the first problem from curriculum/track.md.`

Run `python3 scripts/roll-stats.py` to create `state/stats.json`.

Commit `setup: initialized state`.

---

## Closing

Tell them, in this order: what level you set, how many problems are in their track, which pattern they start on, and the one rule that matters —

> One thing before we start: I won't write solution code for you until you've submitted an accepted answer on LeetCode. You get five hints, each more specific than the last, and then I stop. That's not me being difficult — it's the only version of this that actually makes you better. After you've got it accepted, I'll review your code and show you the canonical optimal.

Then offer the first problem.

## This skill ends when

All six phases verified and committed. Route to `skills/daily-drill`.
