---
name: daily-drill
description: >
  Picks today's problem set. Triggers on: "today", "what should I do", "give me problems",
  "next", "daily", "what's next", "let's practice". Reads curriculum/track.md, the revisit
  queue from question frontmatter, and the daily budget from config/user.json. Respects
  the difficulty ramp — never serves a Hard to someone who hasn't cleared 2 Mediums in
  that pattern. Hands off to teach-problem at S0.
---

# Daily Drill Skill

Picks what to work on today. Does not teach — hands off to `teach-problem`.

## Read order

1. `state/current.json` — if something is active, **offer to resume it instead**. Don't start a second problem on top of an unfinished one.
2. `config/user.json` — `daily_budget_problems`
3. `state/stats.json` — per-pattern mastery
4. `curriculum/track.md` — the ordered path
5. Question frontmatter across `questions/**` — for `revisit_on <= today`

## Selection order

Fill the daily budget in this priority:

| Priority | Take | Cap |
|---|---|---|
| 1 | **Revisits due** (`revisit_on <= today`, `status: solved`) | Max 1 per day. More and it becomes revision instead of progress. |
| 2 | **Parked problems** older than 3 days | Max 1. Parked work rots. |
| 3 | **Next in track** | Fill the remaining budget |

## The difficulty ramp — the rule this system exists for

Before serving a problem, check the learner's history **in that pattern**:

| They want | Required first |
|---|---|
| A Medium | ≥2 Easy solved in this pattern, OR ≥3 Medium solved in a pattern this one depends on |
| A Hard | ≥2 Medium solved **in this pattern specifically** |

| Check fails | Do |
|---|---|
| Ramp not met | Say so plainly and offer the bridging problem instead. "You've done one Easy in sliding window. Jumping to Minimum Window Substring is the jump that makes people quit. Longest Repeating Character Replacement first — it's the same invariant with one extra term." |
| They insist | Serve it, but record `ramp_override: true` in the question frontmatter so the progress report tells the truth later. |
| **no data for the pattern** | Start at the easiest in that pattern. Never guess they're ready. |

Never schedule a pattern before its `depends_on` patterns have ≥2 solved. `config/patterns.json` holds the graph.

## Paid-only problems

7 of the 150 are Premium-gated (`paid_only: true` in `merged.json`). Before serving one, ask once whether they have Premium. If not, substitute the nearest free sibling in the same pattern and say you did.

## Output format

```
Today — 2 problems, ~50 min

1. REVISIT · Two Sum (#1) · Easy · 01-arrays-hashing
   Solved 21 days ago with 0 hints. Quick re-derive, not a re-solve.

2. NEW · Longest Repeating Character Replacement (#424) · Medium · 03-sliding-window
   Ramp: you have 2 Easy in this pattern. This is the bridge to Minimum Window.
   https://leetcode.com/problems/longest-repeating-character-replacement/

Say "start" for #2, or name either one.
```

Keep it to what fits the budget. Do not offer six problems to someone whose budget is two — a list that can't be finished is a list that gets abandoned.

## This skill ends when

They pick one. Route to `skills/teach-problem` at S0 with that slug.
