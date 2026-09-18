---
name: pattern-brief
description: >
  Teaches or writes up a pattern in the abstract, independent of any single problem.
  Triggers on: "explain sliding window", "what is a monotonic stack", "when do I use
  binary search", "I keep confusing X and Y", "pattern brief", "how do I recognize".
  Reads and writes patterns/<slug>.md. Use for pattern-level questions; use
  teach-problem for a specific problem.
---

# Pattern Brief Skill

A pattern brief is the transferable asset. A solved problem teaches you one problem; a pattern brief teaches you the next twenty.

## Read order

1. `config/patterns.json` — the entry for this pattern
2. `patterns/<slug>.md` — if it exists
3. `questions/<NN>-<pattern>/` — which ones they've actually solved; use those as examples, since a sibling they solved is worth five they haven't

Don't read `merged.json` unless you're listing problems.

## If the brief doesn't exist yet

Delegate to the `pattern-researcher` agent. It writes `patterns/<slug>.md` and returns a path plus a short summary. Then deliver the content in your own voice, adapted to their level.

## Brief structure — fill every section

```markdown
# <Pattern Name>

_Pattern id: 03-sliding-window · Depends on: 02-two-pointers · Problems solved: 3/6_

## The one-sentence idea
[What it fundamentally does. If you can't say it in one sentence you don't have it yet.]

## How to recognize it
[The signals. This is the most valuable section — it is what makes pattern recognition
possible. Phrase each as something visible in a problem STATEMENT, not in a solution.]
- ...

## The invariant
[One sentence. What is always true, that everything else exists to maintain.]

## The shape
[The algorithm's skeleton in English. Never in code — a brief is read at S1, when code
is still forbidden.]

## Where it breaks
[When this pattern does NOT apply, and what it gets confused with. A pattern you can't
rule out is a pattern you can't rule in.]

## Confusable with
| Also looks like | Tell them apart by |
|---|---|

## Complexity
[Typical time and space, and what drives each.]

## Common traps
[From config/patterns.json plus anything they personally got wrong — check the
`## Defects Found` tables in their solved question files. Their own past mistakes are
worth more here than generic ones.]

## Problems in this pattern
| Problem | Difficulty | Status |
|---|---|---|
```

## Teaching a pattern out loud

Order matters, and it is the opposite of how most courses do it:

1. **A problem they can already solve badly.** Start from the brute force they'd write.
2. **Where the waste is.** Make them see the redundant work before you name the fix.
3. **The invariant.** Now it lands, because they know what it's for.
4. **The signals.** Only now — recognition makes sense once they know what they're recognizing.
5. **Two siblings.** One they've solved, one they haven't.

Never open with the definition. A definition given before the need is a definition that doesn't stick.

## "I keep confusing X and Y"

This is the highest-value question a learner asks. Answer it with a discriminator table, not two descriptions:

| If the problem says | It's X | It's Y |
|---|---|---|
| contiguous subarray | sliding window | — |
| any pair, order irrelevant | — | two pointers on sorted |

Then give one problem for each and ask them to classify a third, cold.

## After writing

Commit `pattern: <slug> brief`. Update `Problems solved: n/m` in the metadata line whenever it changes.

## This skill ends when

The brief is written or updated and delivered. If they came here mid-problem, return them to their stage — restate the stage banner.
