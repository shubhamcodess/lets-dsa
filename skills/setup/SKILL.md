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
| Fails | Report the actual error, then run the checks below. **Do not tell them to restart the session** until you have confirmed the config is actually loadable — a restart on a broken config wastes their tokens and changes nothing. |

**If `get_daily_challenge` fails, check these in order — the first two are silent failures:**

1. **Is `.mcp.json` at the PROJECT ROOT?** Claude Code reads project MCP servers only from `<project>/.mcp.json`. There is no setting that points elsewhere. A config in a subfolder is never read and the server simply never appears — not failed, not pending, absent.
2. **Have the project's MCP servers been approved?** Claude Code asks once per project before starting servers from `.mcp.json`. If it was declined, the server stays absent. `/mcp` shows the current state.
3. **Does the server actually launch?** From the project root:
   ```
   npx -y @jinzcdev/leetcode-mcp-server@1.4.0 --site global
   ```
   It should start and wait. Ctrl-C to exit. If npx fails, it is Node or network, not Claude Code.
4. Only after 1–3 are confirmed is a restart worth spending.

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

This takes 3–5 minutes — it fetches 7 sheets and verifies every slug against LeetCode's public GraphQL. Behind a corporate TLS proxy it prints a one-line note about falling back to the macOS trust store; that is expected, and verification stays on. Report the real numbers it prints: total, per-pattern counts, anything dropped.

| Result | Do |
|---|---|
| All verified, 0 dropped | Say so, with the real count. Continue. |
| Some dropped | Name them. They're excluded from the track. That's correct behaviour, not a failure. |
| Network failure | Report it. Offer to run without `--verify` — the track still works, just without ids and tags. |

Then build the foundations layer:

```
python3 scripts/build-foundations.py
```

Report the real numbers: 8 topics, total minutes, and how many free links. Tell them
plainly that `01-complexity-analysis` gates every pattern and `05-basic-recursion` gates
five — those two are the ones that decide whether the rest of the curriculum works.

Then build the ladder:

```
python3 scripts/build-track.py
```

This writes `curriculum/track.md` — the actual order of work. Report the real output: 6 tiers,
the floor (90), interview-ready (180) and strong (250) totals.

**Say this plainly, because the number misleads otherwise:** 90 is the floor — every pattern
met once. It is *not* interview-ready. 180 is, and it is weighted toward the patterns the
curated sheets actually invest in (Trees is 15% of all sheet weight; fast-slow pointers is 1%).

The generated track already encodes:
- Pattern order from `depends_on` — never a pattern before its prerequisites
- Foundation gates before the patterns they gate
- Easy → Medium → Hard inside each pattern, never a raw jump
- Sheet consensus picking which problem at a given difficulty

If their `timeline_weeks × 7 × daily_budget_problems` is below 180, tell them what that
actually buys — floor coverage, or depth in fewer patterns — and let them choose. Do not
silently rescope.

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

Run these to create the remaining state files:

```
python3 scripts/roll-stats.py
python3 scripts/confusion.py
```

`confusion.py` will report zero of everything — correct on day one. It fills in as defects
get recorded at S4 and wrong pattern guesses at S1.

Commit `setup: initialized state`.

---

## Two things to tell them about how the teaching adapts

**If you set them to `beginner`:** say that the first problem in each new pattern will be
fully worked by you as a demonstration, the second will be partially worked, and from the
third on they are on their own. This is deliberate — novices retain 20–40% more from a
worked example than from unguided struggle, and that advantage disappears as they improve.
It fades per pattern, automatically. **At `intermediate` or `advanced` it never happens.**

**Everyone:** revisits are scheduled by `scripts/schedule.py` from how the solve actually
went — hints used and attempts — not from a fixed calendar and not from how it felt. A
problem they needed four hints for comes back in days; one they solved cold comes back in
weeks.

## Closing

Tell them, in this order: what level you set, how many problems are in their track, which pattern they start on, and the one rule that matters —

> Two things before we start. First, you'll be explaining your thinking out loud at every
> stage, and I'll grade the explanation — not just whether the code works. Solving silently
> is the most common way strong coders fail interviews, and it's the cheapest thing to fix.
>
> Second: I won't write solution code for you until you've submitted an accepted answer on LeetCode. You get five hints, each more specific than the last, and then I stop. That's not me being difficult — it's the only version of this that actually makes you better. After you've got it accepted, I'll review your code and show you the canonical optimal.

Then offer the first problem.

## This skill ends when

All six phases verified and committed. Route to `skills/daily-drill`.
