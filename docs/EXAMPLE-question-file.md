# What a completed question file looks like

**This is documentation, not progress.** It is an illustrative example of a finished
`questions/**/*.md`. It lives in `docs/` precisely so it is never counted by
`roll-stats.py`, which only reads `questions/`.

---

```markdown
---
problem: longest-substring-without-repeating-characters
leetcode_id: 3
title: Longest Substring Without Repeating Characters
difficulty: Medium
pattern: 03-sliding-window
status: solved
stage_reached: S6_RECORD
mode: teach
first_touched: 2026-09-18
solved_on: 2026-09-18
accepted_verified: self-reported
hints_used: 2
attempts: 3
revisit_on: 2026-09-28
---

# Longest Substring Without Repeating Characters (#3)

_Pattern: Sliding Window · Difficulty: Medium · Status: solved_

## Problem
Longest run of characters with no repeats. n up to 5·10^4, so O(n²) is out.
https://leetcode.com/problems/longest-substring-without-repeating-characters/

## Examples
| Input | Output | Why |
|---|---|---|
| "abcabcbb" | 3 | "abc" — the second "a" forces the window to move |
| "bbbbb" | 1 | every extension breaks the rule immediately |
| "" | 0 | nothing to measure |

## Pattern Signal
It asks for a *contiguous* run, and the thing that disqualifies a run — a repeat — can
be fixed by dropping characters from the front. That's grow-right/shrink-left.

## Intuition
The window never contains a duplicate. When adding a character breaks that, I move left
forward until it's true again. Every character enters once and leaves once, so it's one
pass even though there are two pointers.

## The Ladder
| Tier | Approach | Time | Space |
|---|---|---|---|
| Brute | every substring, check each for duplicates | O(n³) | O(n) |
| Better | every start, extend until a repeat | O(n²) | O(n) |
| Optimal | sliding window, remember last index of each char | O(n) | O(min(n, charset)) |

What optimal buys: better still rescans from each start. Optimal never re-examines a
character it has already passed — left only moves forward.

## My Pseudocode
1. left = 0, best = 0, seen = empty lookup
2. for right over the string:
3.   if current char is in seen AND its last index >= left:
4.     left = that index + 1
5.   record current char's index in seen
6.   best = max(best, right - left + 1)
7. return best

## Defects Found
| Line | Class | What it was |
|---|---|---|
| 3 | INVARIANT-BROKEN | first version dropped the `>= left` check, so a stale index from before the window dragged left backwards. Broke on "abba". |
| 6 | OFF-BY-ONE | had `right - left` — window length is inclusive on both ends. |

## My Solution
[the accepted code]

## Canonical Optimal
[the canonical version]

## Complexity
| | Time | Space |
|---|---|---|
| Mine | O(n) | O(min(n, 128)) |
| Canonical | O(n) | O(min(n, 128)) |

## Notes to Future Me
The bug that cost me two attempts was letting `left` move backwards. Any time I store an
index and compare against a pointer, the question is whether that index is still inside
the window. "abba" is the input that catches it.

Transfer: same shape as Longest Repeating Character Replacement and Minimum Window
Substring — the difference is only what breaks the invariant and what repairs it.

## Session Log
<!-- Format: [date] S<n> — [what happened] -->
- 2026-09-18 S1 — named the pattern from "contiguous", missed the constraint signal first time
- 2026-09-18 S2 — traced "abcabcbb" clean; the break question caught the stale-index case
- 2026-09-18 S4 — 2 rounds, both defects above
- 2026-09-18 S6 — accepted on attempt 3, 2 hints
```

---

## What to notice

- **Everything in `## Pattern Signal`, `## Intuition` and `## Notes to Future Me` is in the learner's words.** Claude never writes those sections. They are the reason the file is worth keeping.
- **`## Defects Found` is the most re-readable table in the file.** It records how *this person specifically* gets things wrong, and `pattern-researcher` reads it back into the pattern brief's common traps.
- `## Canonical Optimal` stays empty until S6. Filling it earlier would be the guardrail failing.
