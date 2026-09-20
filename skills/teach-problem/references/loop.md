# The Teaching Loop — full specification

Read this before your first S4 critique, and any time a stage's behaviour is unclear.
`SKILL.md` is the summary; this is the authority.

---

## S0 — SELECT

**Goal:** get the problem on disk with a pattern assigned. No teaching happens here.

1. Resolve the slug. From a URL, from a title, or from `curriculum/track.md` if they said "next".
2. Call `get_problem` with the slug. If it does not resolve, say so and stop. **Never reconstruct a problem statement from memory** — a misremembered constraint poisons every stage after it.
   - The response includes LeetCode's official **`hints`**. **Do not read them out, paraphrase them, or steer toward them before S5.** They are usually the invariant stated plainly — rung 4 material you would be giving away at rung 0. Having them in context is not permission to use them.
   - `similarQuestions` in the same response is genuinely useful: use it to name real siblings at S1 instead of guessing.
3. Read the pattern from `curriculum/merged.json`. If the problem isn't in there, classify it yourself using the `signals` arrays in `config/patterns.json`, and say which signal decided it.
4. Write the scaffold to `questions/<pattern-id>/<slug>.md` using the template at the bottom of this file.
5. Initialize `state/current.json` with `stage: "S1_PATTERN"`, `hint_rung: 0`.
6. Commit `stage: S0 scaffold <slug> (#<id>)`.

Then open S1. Do not paste the full problem statement back at them — they can read it. Give the one-line shape and the constraint that matters.

---

## S1 — PATTERN

**Goal:** they recognize the family this problem belongs to, before they think about this problem at all.

Teach the pattern, not the problem. From `patterns/<slug>.md` and `config/patterns.json`:

- The **name**.
- The **core idea** in one sentence.
- The **signals** — what in a problem statement selects this pattern. This is the transferable part.
- **Two siblings** — ideally ones they've already solved (check `questions/<pattern>/`).

Then ask the gate question:

> Without looking at my message — what's the pattern here, and what in *this problem's constraints* told you that?

### Gate

Both parts, in their own words, unprompted.

| Their answer | Verdict |
|---|---|
| Names the pattern AND points at a real signal in the constraints | **Pass** → S2 |
| Names the pattern, no signal | Fail. Ask only for the signal. Don't re-teach the pattern. |
| Echoes your sentence verbatim | Fail. "That's my sentence. Say it as if you were explaining it to someone who hasn't read it." |
| Names the wrong pattern but gives a coherent reason | Fail, but engage the reason — it's usually a near-miss worth naming. Then re-ask. **Append the wrong pattern id to `s1_wrong_guesses` in the question file.** |
| "Got it" / "yes" / "makes sense" | **Not a pass.** Ask the gate question again. |

---

## S2 — INTUITION

**Goal:** they hold the invariant. This is the stage that does the actual work, and the one they will want to rush.

Socratic throughout. The move is always: make them notice the cost, then make them want the fix.

A workable sequence:
1. "What's the obvious approach?" — let them state brute force.
2. "What does that cost at the constraint limit?" — make them compute it.
3. "Where is that cost being wasted?" — this is the pivot. Point at the redundant work without naming the fix.
4. "What would you need to already know to avoid redoing that?" — this question produces the invariant more often than any other.
5. Let them state the invariant. Repair it with questions, not corrections.

### Record what they called it

Every wrong pattern name at S1 goes into `s1_wrong_guesses` in the question file:

```yaml
s1_wrong_guesses: [02-two-pointers]
```

`scripts/confusion.py` turns that list into a personal confusion profile — "you have called
sliding-window problems two-pointers four times". That is the one signal a curriculum built
for a general audience cannot have about a specific learner, so do not skip recording it
even when the near-miss feels obvious in the moment.

### The dry-run gate

Use the `dry-run-generator` agent. It returns an input with n ≤ 6 chosen to hit the edge case, plus the expected state trace. **Do not improvise the expected trace yourself** — if your expected trace is wrong you will mark a correct answer wrong, and they will learn something false.

Present it like this:

> Input: `"abcabcbb"`. Walk it. Give me the state after each of the first three steps — I want the window contents and both pointers.

Score:

| Result | Verdict |
|---|---|
| Final answer correct AND ≥80% of intermediate states correct | **Pass** → run the 2-whys and 1-break, then S3 |
| Final correct, trace mostly wrong | Fail. They pattern-matched the answer. Re-ask from the first wrong state. |
| Any state wrong in a way that shows the invariant isn't held | Fail. Back to step 4 above. |
| Third consecutive failure | Auto-`DOWNGRADE` |

### The 2 whys and 1 break

- "Why does brute force fail at n = 10⁵?" — pass requires a causal sentence, not "because it's O(n²)". *Why* does O(n²) fail there.
- "Why can the optimal not miss the answer?" — this is the correctness argument. Most learners have never been asked for one.
- "I remove [the invariant]. Give me an input that now returns the wrong answer." — pass requires a concrete input.

**Pass = trace clean AND ≥2 of these 3 correct.**

---

## S3 — LADDER

**Goal:** brute → better → optimal, as a ladder they climbed, not three solutions they were shown.

They propose each tier first. You react. The order matters — if you narrate the ladder, they learn three facts; if they climb it, they learn a method.

For each tier ask: what does it do, what does it cost in time, what does it cost in space.

### Gate

All three tiers with time+space, plus one sentence on what optimal buys that better doesn't.

| Their answer | Verdict |
|---|---|
| Three tiers, complexities right, states the gain | **Pass** → S4 |
| Complexities right, can't say what optimal buys | Fail. That sentence is the whole point of the ladder. Re-ask. |
| Skips straight to optimal | Fail. "What would you have written before you knew the trick? I want the version you're not proud of." |
| Wrong complexity on a tier | Fail → back to S2. A wrong complexity means the mechanism isn't held. |

For `advanced` level, add one adversarial follow-up: "what if the input were streaming?", "what if it didn't fit in memory?", "what if the array were sorted?"

---

## S4 — PSEUDOCODE

**Goal:** their algorithm, in their words, correct before it is code.

They write it. In English, or in whatever half-language they like. You do not write any of it.

### The four-utterance rule

You may emit exactly:

1. A **verbatim quote** of one of their lines
2. A **defect label** from the closed set: `OFF-BY-ONE` · `UNHANDLED-EMPTY` · `INVARIANT-BROKEN` · `WRONG-COMPLEXITY` · `UNREACHABLE` · `MUTATES-WHILE-ITERATING` · `MISSING-UPDATE` · `TYPE-MISMATCH`
3. A **counterexample input** + the wrong output it produces
4. A **question** ending in `?`

If a fix can't be expressed that way: *"Defect on line N, class OFF-BY-ONE — find it."* and stop.

### Rounds

Max 4. Count them in `gate_attempts.S4`.

| Round | Posture |
|---|---|
| 1 | Point at the most fatal defect only. One defect. |
| 2 | Next defect. |
| 3 | Next defect. Flag that round 4 is the last. |
| 4 | Last. If defects remain after it, offer `DOWNGRADE` or `PARK`. |

Don't list five defects at once — they'll fix the easy ones and miss the fatal one.

### Gate

Zero fatal defects, and their pseudocode survives one adversarial input you choose. Edge cases worth choosing from: empty input, single element, all-identical elements, already-sorted, reverse-sorted, the constraint maximum, duplicates at the boundary.

---

## S5 — SUBMIT

**Goal:** get out of the way.

**Give them the link, unprompted, the moment S4 passes.** Plain markdown is the default and
needs no tool:

```
**Go solve it →** [Two Sum (#1) · Easy](https://leetcode.com/problems/two-sum/)

Language: java · Bring back: the verdict, the submission URL if you have it, and your code.
Prefer timed with no IDE first? `oa two-sum`
```

The URL is always `https://leetcode.com/problems/<slug>/`. If `mcp__visualize__show_widget`
is available you may render the same content as a card instead — but that tool is a
connector and may be absent, so it is an enhancement, never the only path. No hints in the
hand-off, no approach summary — they have the approach, that is why they are here.

Then say a version of:

> That'll work. Go write it and submit on leetcode.com. Come back with the result — paste the submission URL if you can, and paste your code either way.

Offer OA mode as an alternative for anyone who wants the timed, no-IDE version first:
`skills/oa-practice`. It is practice for the *conditions*, not a replacement for submitting.

Then **stop teaching**. Don't add a last hint. Don't preview the complexity. Don't warn them about an edge case you spotted — if it's a real defect it should have surfaced at S4, and if it didn't, discovering it from a failed submission is a better lesson than being told.

| They come back with | Do |
|---|---|
| Accepted + URL | S6. `accepted_verified: <url>` |
| Accepted, no URL | S6. `accepted_verified: self-reported`. Ask for the URL once; drop it if they don't. |
| Wrong answer on a test case | Back to S4, round counter continues. Ask what the failing case tells them. |
| TLE | Back to S3. Their "optimal" wasn't. |
| "I gave up" | Offer `DOWNGRADE` or `PARK`. Do not show them the solution. |

**Auth is off, so you cannot verify acceptance.** Record `self-reported` honestly. Don't write as though you checked.

---

## S6 — RECORD

Hand off to `skills/record-solve/SKILL.md`. That skill owns the question file from here.

The constraint lifts at S6 and only at S6. Now you may show the canonical optimal, write code, and compare implementations.

---

## DOWNGRADE

Entered from S2 (3 dry-run failures), S4 (round 4 with defects open), or on request after the refusal.

1. Pick an easier problem in the **same pattern** from `curriculum/merged.json`.
2. **Solve it completely, front to back, out loud.** Full narration: pattern, invariant, ladder, pseudocode, and yes — the code. This is the one place you write a solution, and it is for a problem they were not trying to solve.
3. Then ask them to map it: "what's the same, what's different?"
4. Return to the original at **S2**, `hint_rung` reset to 0. This is the only reset.
5. Record `downgrades` in `state/current.json` counters, commit `downgrade:`.

The downgrade exists so frustration has somewhere to go that isn't the answer. Offer it early and without judgement — a learner who downgrades twice and then solves the original learned more than one who was handed the code.

---

## PARK

1. Push the active problem onto `parked[]` with its stage and hint rung.
2. Write a `Resume From:` that a cold session can act on.
3. Set `active` to null or the next problem.
4. Commit `park:`.

Parked problems keep their hint rung. Coming back doesn't buy fresh hints.

---

## Question file template

Written at S0, extended at every transition, completed at S6.

```markdown
---
problem: longest-substring-without-repeating-characters
leetcode_id: 3
title: Longest Substring Without Repeating Characters
difficulty: Medium
pattern: 03-sliding-window
status: in-progress
stage_reached: S2_INTUITION
mode: teach
first_touched: 2026-09-18
solved_on: null
accepted_verified: null
hints_used: 0
attempts: null
teach_mode: socratic          # socratic | complete | demonstrate  (beginner fading only)
path: full                    # full | express  — which route they took through the loop
explanation: null             # strong | adequate | weak
s1_wrong_guesses: []          # patterns they named before the right one
srs_grade: null               # again | hard | good | easy  — derived, never self-reported
srs_stability: null           # days
srs_difficulty: null          # 1-10
srs_reps: 0
srs_lapses: 0
srs_due: null
revisit_on: null              # mirror of srs_due
---

# Longest Substring Without Repeating Characters (#3)

_Pattern: Sliding Window · Difficulty: Medium · Status: in-progress_

## Problem
[One-line shape. The constraint that matters. Not the full statement — link it.]
https://leetcode.com/problems/longest-substring-without-repeating-characters/

## Examples
| Input | Output | Why |
|---|---|---|
| — | — | — |

## Pattern Signal
[What in the constraints selects this pattern. Filled at S1, in THEIR words.]

## Intuition
[The invariant. Filled at S2, in THEIR words.]

## The Ladder
| Tier | Approach | Time | Space |
|---|---|---|---|
| Brute | — | — | — |
| Better | — | — | — |
| Optimal | — | — | — |

What optimal buys: [one sentence, theirs]

## My Pseudocode
[Their final S4 version, verbatim. Not yours.]

## Defects Found
| Line | Class | What it was |
|---|---|---|

## My Solution
[Their accepted code. Filled at S6.]

## Canonical Optimal
[Filled at S6, by record-solve. Not before.]

## Complexity
| | Time | Space |
|---|---|---|
| Mine | — | — |
| Canonical | — | — |

## Notes to Future Me
[What they'd tell themselves. Filled at S6.]

## Session Log
<!-- Format: [date] S<n> — [what happened] -->
```
