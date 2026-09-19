---
name: oa-practice
description: >
  Online-assessment simulator. The learner writes real code in a bare in-chat editor with
  no autocomplete, no highlighting and no feedback, then it is compiled and run. Triggers
  on: "oa", "oa mode", "timed coding", "let me actually code this", "practice writing
  code", "mock OA", "google doc round", "assessment practice", and from interview-mode's
  coding phase. Java, C++, TypeScript and Python. Owns state/oa-attempts.json.
---

# OA Practice Skill

Tests something no other mode here does: can you write **correct code** with no IDE, no red squiggles and no autocomplete. Strong LeetCoders fail online assessments and Google-Doc rounds on exactly this.

## The one rule

**Nothing is shown while they type. Not a hint, not a syntax note, not "careful with that bound".**

This is structural, not willpower — the widget holds no compiler and makes no calls. Your job is not to undermine it: do not read their partial code and comment on it, and do not answer "does this look right?" with anything but *"submit it and find out."*

## Flow

| Step | You do |
|---|---|
| 1 | `get_problem` the slug. Pull `codeSnippets` for all four languages and the statement. |
| 2 | Render the editor widget — statement, timer, language selector, stub pre-filled. |

**No pre-submit affordances of any kind.** No brace counter, no bracket matching, no
character count, no "looks unbalanced" nudge. Anything that tells the learner something
about their code before they submit is the mode failing at its one job — an assessment
gives you a blank box and silence. Compilation failing *at submit* is the feedback.

**The timer must persist across re-renders.** A widget's script restarts whenever the chat
re-renders it, so a `t0 = Date.now()` set at load resets to zero and every attempt after the
first records a meaningless duration — silently corrupting the time-to-first-correct metric.
Store the start time in `localStorage` beside the draft and read it back:

```js
var t0; try { t0 = +localStorage.getItem('oa:t0:' + SLUG); } catch(e) {}
if (!t0) { t0 = Date.now(); try { localStorage.setItem('oa:t0:' + SLUG, t0); } catch(e) {} }
```

Clear that key only when the problem is finished, not on submit — a retry is the same sitting.

**Check whether a resubmission actually changed.** If the code is byte-identical to the
previous attempt, say so and report the same verdict without pretending it is new
information. Resubmitting unchanged code is itself a habit worth naming.
| 3 | **Say nothing** until they submit. If they ask how it's going, that is the answer above. |
| 4 | They submit → the widget sends `OA SUBMIT <slug> lang=<l> elapsed=<n>s` plus their code. |
| 5 | Write their code to a scratch file. Run the command below. |
| 6 | Report the verdict verbatim from the output. Offer a retry. |

```
python3 scripts/oa-run.py --slug <slug> --lang <lang> --file <scratch>.<ext> \
    --tests <tests>.json --record --elapsed <n>
```

`--record` appends to `state/oa-attempts.json` itself, so the evidence does not depend on you remembering.

## Test cases

`--tests` takes `[{"input": ["[2,7,11,15]", "9"], "expected": "[0,1]"}]`.

| Source | When |
|---|---|
| The `## Examples` table in the question file | always — these are the 3 LeetCode examples |
| Edge cases you generate | at submit, once they have finished coding |

**Generate the edge cases only at submit, never before** — deciding what to test is part of what is being assessed. Draw from: empty, single element, all identical, already sorted, reverse sorted, duplicates at the boundary, the constraint maximum.

To know the expected output for a generated case you must solve the problem. That is allowed here **only at submit time**, the same position as S6. Write the reference into the scratchpad, use it as an oracle, and **never show it, quote it, or describe its approach.** Report only pass/fail and the failing input.

## Reporting — terse, no commentary

Relay the runner's output and **stop**. No encouragement, no progress notes, no "good, it
compiles further than last time", no framing of what improved. An assessment prints a
verdict and says nothing else, and commentary here is coaching wearing an OA costume.

Forbidden in a verdict message: "progress", "good", "nearly", "that's movement", "still
yours to fix", any comparison to a previous attempt beyond the bare `attempt N`, and any
restatement of what the compiler already said.

Permitted: the runner's output, the attempt number, and one line offering a retry.

Explanation belongs **after** the loop, not here — `record-solve` at S6 is where the code
gets reviewed, the canonical optimal is shown, and complexity is compared. Keeping OA mode
silent is what makes that review worth having.

```
COMPILED          yes
TESTS             5/7 passed
  FAIL  input: []      -> 0     expected: -1
TIME              14m 22s · attempt 2
```

| Outcome | Say |
|---|---|
| Compile error | Show it — the runner already remaps line numbers to *their* file. At a real OA this is a zero. |
| Wrong answer | Name the failing input. **Do not say why it fails.** |
| Accepted | Say so. Then: which edge case did they nearly miss, and did they test before submitting? |

Unlimited retries, every one recorded. "Passed on attempt 4" is the signal, not a failure.

## Not supported yet

`oa-run.py` refuses these rather than mis-harnessing them, and tells you which:

- **Design problems** (LRU Cache style — constructor plus an operation sequence)
- **`ListNode` / `TreeNode`** — needs a node deserializer per language

When refused, say so plainly and offer the problem on leetcode.com instead. Do not improvise a harness.

## After

Offer `record-solve` if this was a curriculum problem they had reached S5 on. An OA attempt is evidence of coding-under-pressure; it is **not** a substitute for the S0–S6 loop, and a problem solved only in OA mode has not been understood, only typed.

## This skill ends when

The verdict is delivered and the attempt is in the ledger. Route back to `daily-drill` or `interview-mode`.
