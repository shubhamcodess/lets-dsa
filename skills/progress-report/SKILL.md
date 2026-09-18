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

## Read order

1. `state/stats.json`
2. Question frontmatter across `questions/**` — `status`, `hints_used`, `attempts`, `ramp_override`, `mode`
3. `config/patterns.json` — for the dependency graph
4. `config/user.json` — targets and timeline

Run `python3 scripts/roll-stats.py` first if `stats.json` is older than the newest question file.

## Mastery per pattern

Mastery is not a solve count. A problem solved at hint rung 5 after four attempts is not the same as one solved cold.

| Signal | Weight |
|---|---|
| Solved with 0–1 hints | Full credit |
| Solved with 2–3 hints | Partial |
| Solved with 4–5 hints, or after a downgrade | Exposure only, not mastery |
| `ramp_override: true` | Discount it and say why |
| `mode: review-only` | Doesn't count toward mastery — they didn't go through the loop |
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
your 150 — the largest single block you haven't started.

## Readiness verdict
**Not yet.** For Google-level, DP and graphs are near-certain to appear and you have 1
solved across both. Two patterns solid out of the six that matter most.

Earliest realistic: 6-7 weeks at 2/day, if the next 3 weeks are DP and graphs.

## This week
1. 17-1d-dp — 4 problems, Easy to Medium. Climb House Robber before Coin Change.
2. Revisit due: Two Sum (#1), Valid Anagram (#242)
3. Then interview mode on sliding window — it's ready to be tested under pressure.
```

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
