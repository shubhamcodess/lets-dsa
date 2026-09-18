---
name: foundations
description: >
  Teaches the prerequisite topics a learner needs BEFORE solving problems — complexity
  analysis, recursion, hashing, sorting, collections, basic maths, language basics,
  loop/pattern thinking. Triggers on: "basics", "foundations", "where do I start",
  "I'm new to DSA", "teach me recursion", "explain big O", "I don't know the basics",
  "prerequisites", and automatically whenever daily-drill hits an ungated topic.
  Reads config/foundations.json. Owns topics/<id>.md.
---

# Foundations Skill

The layer before the loop. Problems assume these; a learner who skips them stalls at the first Medium and thinks they're bad at DSA when they're actually missing a prerequisite.

## Read order

1. `config/foundations.json` — the 8 topics, what each gates, and its free resources
2. `topics/*.md` — which are already learned
3. `config/user.json` — level and language

Do **not** read `curriculum/merged.json` here. Foundations are topics, not problems.

## The eight topics

| Topic | Gates | Time |
|---|---|---|
| `00-language-basics` | — | 120m |
| `01-complexity-analysis` | **every pattern** | 90m |
| `02-logical-thinking` | — | 150m |
| `03-collections` | arrays-hashing | 120m |
| `04-basic-maths` | bit-manipulation, math-geometry | 90m |
| `05-basic-recursion` | trees, backtracking, graphs, 1d-dp, 2d-dp | 180m |
| `06-basic-hashing` | arrays-hashing, sliding-window | 90m |
| `07-sorting` | two-pointers, binary-search, intervals, greedy | 150m |

`01-complexity-analysis` gates everything and is non-negotiable. The S3 ladder gate asks for time and space on three approaches — without this topic that gate is unpassable, and the learner cannot tell a correct solution from a lucky one.

`05-basic-recursion` gates five patterns, more than any other. Trees, backtracking, graphs and DP are all recursion wearing different hats.

## Teaching a topic — five steps, in this order

1. **Why it exists.** Read `why_first` from `config/foundations.json` and say it in your own words. A learner who doesn't know why they're learning something learns it badly.
2. **The idea**, pitched at their level. One concept at a time.
3. **The free resources.** Each topic carries Striver article and video links in `resources`. **Paste the links. Do not read them and relay the contents** — that turns a 20-minute video they'd remember into a paragraph they won't.
4. **They do the exercises.** `exercises` lists what to work through. These are practice, not gated problems — no S0–S6 loop here.
5. **The comprehension check** below.

## The comprehension check

Same principle as the problem loop: **nothing passes on "got it".** A produced artifact only.

| Topic | The check |
|---|---|
| `01-complexity-analysis` | Give them a nested loop where the inner bound depends on the outer. They state the complexity **and** justify it by counting. Then: "constraints say n ≤ 10^5 — what complexity do you need, and how do you know?" |
| `05-basic-recursion` | They hand-trace a recursion, drawing the call stack at its deepest point, and state the base case and why it terminates. |
| `06-basic-hashing` | "Here's an O(n²) nested scan. Make it one pass. What are you trading?" |
| `07-sorting` | "Sorting costs n log n. Name three things that become possible once data is sorted, and one problem where sorting would be the wrong move." |
| `03-collections` | Cost of insert, lookup and delete for list vs set vs map — from memory, then: "where does picking a list instead of a set turn O(n) into O(n²)?" |
| `04-basic-maths` | Extract digits of a number without converting to a string, and say where overflow would bite. |
| `00-language-basics`, `02-logical-thinking` | They write a nested-loop pattern unaided and state its cost. |

Pass = correct **and** justified. "Because it's O(n²)" is not a justification — *why* is it.

## Topic file — write at start, complete at pass

`topics/<id>.md`:

```markdown
---
topic: 05-basic-recursion
name: Recursion & the Call Stack
status: learned
started: 2026-09-18
learned_on: 2026-09-19
check_passed: true
gates_patterns: [09-trees, 12-backtracking, 13-graphs, 17-1d-dp, 18-2d-dp]
---

# Recursion & the Call Stack

## Why this first
[in your words]

## What I understood
[THEIR words. Not yours. This is the section worth re-reading.]

## The check
[what they were asked, what they answered]

## Where I got stuck
[the honest bit — most useful thing in the file six weeks later]
```

`status`: `not-started` | `in-progress` | `learned`

Commit `topic: 05-basic-recursion — learned`.

## The gate

`daily-drill` calls this skill when a pattern's gating topics aren't learned. When that happens:

1. Say plainly which topic is missing and which pattern it gates.
2. Offer to cover it now — give the time estimate from `est_minutes`.
3. **If they insist on the problem anyway:** serve it, but set `foundation_override: true` in the question's frontmatter so `progress-report` reports honestly later.

Say it once, without nagging:

> Before Trees — you haven't covered recursion, and trees are recursion with a shape. About 3 hours, and it also unlocks backtracking, graphs and both DP patterns. Do that first, or push ahead and pick it up as we go?

Both answers are fine. Pushing ahead with a recorded override is better than a lecture.

## Do not

- **Do not run the S0–S6 loop here.** Foundations are topics; there is no LeetCode submission and no hint ladder.
- **Do not apply the no-code rule here.** Explaining recursion with code is the point. The no-code guardrail is about *problem solutions*, not concepts. Write all the illustrative code the topic needs.
- **Do not read and relay the linked articles or videos.** Paste the links.
- **Do not let a learner mark a topic learned without the check.** That's how someone arrives at DP having "done" recursion.

## This skill ends when

The topic file is written and committed. Return to `daily-drill` for the problem that was gated.
