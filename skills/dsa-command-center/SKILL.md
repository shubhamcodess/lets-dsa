---
name: dsa-command-center
description: >
  The orchestrator. Invoke when the intent is unclear, when the learner opens a session
  without a specific ask, or when routing between skills. Triggers on: "what now",
  "where was I", "status", "help", "what can you do", "let's start", "I don't know what
  to work on", and any first message of a session that isn't a specific problem.
  Routes to the other eight skills. Does not teach anything itself.
---

# DSA Command Center

Routing only. This skill picks the right skill and gets out of the way.

## Read order

1. `state/current.json`
2. `state/current.md` (`Resume From:`)
3. `config/user.json`

Nothing else. Don't load the curriculum or pattern briefs to route.

## Routing table

| They said | Route to |
|---|---|
| Nothing configured / first run | `skills/setup` |
| "today", "what should I do", "give me problems" | `skills/daily-drill` |
| "next" | `skills/daily-drill` → then `skills/teach-problem` at S0 |
| A problem name, URL, "teach me", "how do I solve" | `skills/teach-problem` |
| "hint", "stuck", "I don't get it" — **and there is an active problem** | `skills/teach-problem` (hint ladder) |
| "solved", "accepted", "AC", pasting code | `skills/record-solve` |
| "explain <pattern>", "what is sliding window" | `skills/pattern-brief` |
| "show me", "visualize", "animate", "I can't picture it" | `skills/visual-explainer` |
| "interview me", "mock", "practice interview" | `skills/interview-mode` |
| "progress", "how am I doing", "am I ready" | `skills/progress-report` |
| "park", "stop", "later" | `skills/teach-problem` (park path) |
| **anything else** | Ask which of the above they meant. Offer the three most likely. Do not improvise a new workflow. |

## Resume behaviour

If `state/current.json` has an active problem, **resume it** rather than offering a menu:

> `[S2 · INTUITION · hint 2/5]`
> Picking up Longest Substring (#3). You had the invariant and were mid-trace on `"abcabcbb"` — you had it right through index 3, then the left pointer drifted. From index 3: what's the window, and where are both pointers?

Read that directly off `Resume From:`. **Do not re-explain the pattern or restate the invariant** — `Resume From:` records what they already have.

## Status line format

For a bare "status":

```
Level: intermediate · 14 solved across 8 patterns
Active: Longest Substring Without Repeating Characters (#3) — S2 INTUITION, hint 2/5
Parked: Koko Eating Bananas (#875) — S4
Due for revisit: 3
Strongest: 02-two-pointers (5/5) · Weakest: 17-1d-dp (1/12)
```

## This skill ends when

You have routed. Say one line about where you're sending them, then execute that skill. Don't narrate the routing decision at length.
