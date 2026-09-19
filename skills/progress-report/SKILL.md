---
name: progress-report
description: >
  Reports mastery, gaps and interview readiness. Triggers on: "progress", "how am I
  doing", "am I ready", "what's my weakest area", "stats", "report", "how many have I
  solved", "what should I focus on". Reads state/stats.json and question frontmatter.
  Read-only — never modifies state. Gives an honest readiness verdict, not encouragement.
---

# Progress Report Skill

The report exists to tell them something they don't already know. "You've solved 14 problems" is on the counter. What they can't see is whether they'd pass an interview.

## Render the dashboard first

Open with the progress widget **if `mcp__visualize__show_widget` is available** (call
`mcp__visualize__read_me` first). That tool is a connector and may be absent — when it is,
render the same numbers as plain markdown tables. **The report must never be skipped or
thinned because a widget could not render;** the numbers are the point, the card is styling.

Then the prose. The numbers are scannable; the judgement is
not, and the judgement is the part worth reading.

The widget shows: solved against 343, foundations covered, patterns touched, OA attempts, a
position bar against the 90 / 180 / 250 targets, the Easy/Medium/Hard mix, OA metrics
(compiled first try, accepted first submit), and the single biggest blocker. Buttons route
to `basics`, `today` and the full report.

**Never let the bar imply readiness.** Position is a count; readiness is the bands. Put that
sentence next to it whenever the two could be confused.

## Read order

1. `state/stats.json`
2. Question frontmatter across `questions/**` — `status`, `hints_used`, `attempts`, `ramp_override`, `mode`
3. `config/patterns.json` — for the dependency graph
4. `config/user.json` — targets and timeline

Run `python3 scripts/roll-stats.py` first if `stats.json` is older than the newest question file.

## Mastery per pattern

Mastery is not a solve count. A problem solved at hint rung 5 after four attempts is not the same as one solved cold.

`state/stats.json` now also carries `by_difficulty`, `companies_solved`, `oa` and
`position`. Use them:

| Field | Say |
|---|---|
| `by_difficulty` | An Easy-heavy mix is not readiness. Interviews are Medium. |
| `companies_solved` | Only for problems with real company tags — coverage is partial and third-party. Never imply it is complete. |
| `oa.compile_first_try_rate` | Below ~70%, say plainly that at a real OA that is a zero regardless of the algorithm. |
| `oa.accepted_first_submit` | Low means submitting before verifying — a habit, not a knowledge gap. |
| `position.pct_to_interview` | Position, never readiness. |

| Signal | Weight |
|---|---|
| Solved with 0–1 hints | Full credit |
| Solved with 2–3 hints | Partial |
| Solved with 4–5 hints, or after a downgrade | Exposure only, not mastery |
| `ramp_override: true` | Discount it and say why |
| `mode: review-only` | Doesn't count toward mastery — they didn't go through the loop |
| `teach_mode: demonstrate` | **Does not count as solved.** It was a worked example they read. Report it as study, not evidence. |
| `explanation: weak` | Flag it. Silent-solving is the most common way strong coders fail interviews. |
| Revisit passed cold | **Strongest signal available.** Weight it above a first solve. |

| Band | Meaning |
|---|---|
| `solid` | ≥3 solved, average hints ≤1, at least one revisit passed |
| `working` | ≥2 solved, average hints ≤3 |
| `exposed` | ≥1 solved, or solved only with heavy hints |
| `untouched` | 0 solved |

## Output format

```
# Progress — 2026-09-18
_14 solved · 8 of 20 patterns touched · 12 weeks to target_

## Mastery
| Pattern | Solved | Avg hints | Band |
|---|---|---|---|
| 02-two-pointers | 5/5 | 0.8 | solid |
| 03-sliding-window | 3/6 | 2.3 | working |
| 17-1d-dp | 1/12 | 4.0 | exposed |
| 13-graphs | 0/13 | — | untouched |

## What this actually says
You are strong on the linear-scan family — two pointers and sliding window are holding,
and the sliding-window revisit you passed cold last week is the best evidence in here.

The gap is dynamic programming. One problem at 4 hints is not exposure to DP, it's
exposure to me explaining DP. 17-1d-dp gates 18-2d-dp, and between them that's 23 of
your curriculum — the largest single block you haven't started.

## Readiness verdict
**Not yet.** For Google-level, DP and graphs are near-certain to appear and you have 1
solved across both. Two patterns solid out of the six that matter most.

Earliest realistic: 6-7 weeks at 2/day, if the next 3 weeks are DP and graphs.

## This week
1. 17-1d-dp — 4 problems, Easy to Medium. Climb House Robber before Coin Change.
2. Revisit due: Two Sum (#1), Valid Anagram (#242)
3. Then interview mode on sliding window — it's ready to be tested under pressure.
```

## Their error profile — the section nobody else can write

From `state/confusion.json` (regenerate with `python3 scripts/confusion.py`):

```
## What you specifically get wrong
Most frequent defect: INVARIANT-BROKEN (6x) — the invariant is decoration, not something
you are holding. Drill: at S2, do not advance until you can say what breaks if violated.

Confusion: you have called sliding-window problems "two pointers" 4 times. Both move
indices; only one keeps a contiguous range with a maintained property.

Explanation quality: weak on 5 of your last 8. You state complexity only when asked.
```

Lead the report with this once there is enough data. A generic "practice more DP" is
available anywhere; "you break invariants and you under-explain" is not, and it is built
entirely from their own sessions.

**Say nothing here when the data is thin.** An error profile invented from two problems is
worse than no error profile.

## Honesty rules

- **"Am I ready?" gets a real answer.** If they're not ready, say not ready and say what's missing. A soft answer here costs them a real interview.
- **Never round up.** 1 solved at 4 hints is not "getting comfortable with DP".
- **Name the largest gap by blast radius**, not by count — a weak pattern that gates two others matters more than an isolated one.
- **Give the earliest realistic date**, computed from their actual pace, not their hoped pace. If their track needs 3/day and they're doing 1, say that.
- **Credit what's real.** A cold revisit pass is genuinely hard and most learners never test themselves that way. Say so when it happens.

## Read-only

This skill writes nothing except a regenerated `state/stats.json` via the script. Don't touch `current.json`, don't touch question files.

## This skill ends when

The report is delivered. Offer the first item from "This week".
