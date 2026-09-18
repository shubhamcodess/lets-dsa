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

## Foundation gate — check before the difficulty ramp

Read `config/foundations.json` and `topics/*.md`. Before serving a problem, check the
topics that gate its pattern.

| Check | Then |
|---|---|
| `01-complexity-analysis` not learned | **Block.** It gates every pattern, and without it the S3 ladder gate is unpassable. Offer it now — 90 minutes. |
| A pattern-specific gating topic not learned | Say so once, offer it with its `est_minutes`, and let them choose. |
| They choose to push ahead | Serve the problem. Set `foundation_override: true` in its frontmatter so `progress-report` tells the truth later. |
| **no foundations data** | Run `python3 scripts/build-foundations.py`, then re-check. |

Say it once. Don't nag, and don't repeat it every session — a recorded override is better
than a lecture.

> Before Trees — you haven't done recursion, and trees are recursion with a shape. About
> 3 hours, and it also unlocks backtracking, graphs and both DP patterns. Do that first,
> or push ahead and pick it up as we go?

## The three orderings — how "what next" is actually decided

`curriculum/track.md` materializes all of this. Read it rather than re-deriving.

| Question | Decided by | Where |
|---|---|---|
| Which pattern next? | dependency graph, topologically sorted into 6 tiers | `depends_on` in `config/patterns.json` |
| When may I leave a pattern? | 6 problems in tier 1 down to 3 in tier 6, with a required Easy/Medium mix | `TIER_RULES` in `scripts/build-track.py` |
| Which problem inside it? | difficulty ramp first, then sheet consensus | below |
| Is it genuinely held? | mastery band from real hint and attempt counts | `skills/progress-report` |

**The count is the floor, not the proof.** Six solved at hint rung 5 is not a pattern held. `progress-report` bands it `exposed`, and you should say so rather than advancing on the count alone.

## Consensus — which problem inside a pattern

When several problems in a pattern are equally ready to serve, take the one in the most
`lists`. A problem in `neetcode150` + `blind75` + `striver79` + `codingshuttle` is one
four independent curators picked; a problem in one list is one curator's taste.

| lists | Treat as |
|---|---|
| 4+ | Near-certain interview material. Serve first. |
| 2–3 | Core. Standard priority. |
| 1 | Breadth. Serve only once the pattern's consensus problems are done. |

`blind75` and `striver79` are the two strongest single signals — both are explicitly
"if you only have time for N" lists, so membership there means a curator bet scarce time
on it. Say this out loud when you serve one; knowing *why* a problem was chosen is part
of learning to prioritize without help.

**Never use this to skip the ramp.** Consensus picks *which* problem at a difficulty tier,
never *which tier*.

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

Some problems are Premium-gated (`paid_only: true` in `merged.json`). Before serving one, ask once whether they have Premium. If not, substitute the nearest free sibling in the same pattern and say you did.

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
