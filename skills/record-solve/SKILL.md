---
name: record-solve
description: >
  Invoke when the learner reports an accepted LeetCode submission. Triggers on: "solved",
  "accepted", "AC", "got it accepted", "it passed", "done", pasting a submission URL, or
  pasting their working code after S5. Runs stage S6 — reviews their code, shows the
  canonical optimal, records the complexity table, writes the question file and commits.
  This is the ONLY skill permitted to write solution code, and only after acceptance.
---

# Record Solve Skill — stage S6

The constraint lifts here. Now you can write code, show the canonical optimal, and compare.

**Verify first:** `state/current.json` must show `stage: "S5_SUBMIT"` (or `mode: "review-only"`). If it shows an earlier stage, they haven't been through the loop — do not run this skill. Say which gate is still open and route back to `teach-problem`.

---

## Step 1 — Record what actually happened

| They gave you | Write to `accepted_verified` |
|---|---|
| A submission URL | the URL |
| "accepted", no URL | `self-reported` |
| Auth is on and `get_problem_progress` confirms | `verified-YYYY-MM-DD` |

Ask for the URL once. If they don't give it, move on — this is their learning, not an exam. But **never write `verified-` when you did not verify.**

Also capture: attempts, whether they hit TLE or WA first, and `hints_used` from `current.json`.

## Step 2 — Review their code

Use the `submission-grader` agent for the pass, then deliver it yourself.

Report in this order, and keep it to what's true:

1. **Correctness** — does it actually hold the invariant, or does it pass by luck on LeetCode's test set? Name the input that would break it if there is one.
2. **Complexity** — their real time and space. If it differs from what they claimed at S3, say so; that gap is the lesson.
3. **One thing done well.** Specific, not flattery. "You handled the empty case before the loop rather than inside it" beats "nice work".
4. **At most two improvements.** More than two and none land.

Don't rewrite their solution wholesale. Point at lines.

## Step 3 — The canonical optimal

Now show it. Full working code in their language from `config/user.json`.

Then a comparison table — this is the part that builds the pattern library:

| | Time | Space | Difference |
|---|---|---|---|
| Yours | O(n) | O(min(n,m)) | — |
| Canonical | O(n) | O(min(n,m)) | Same shape; canonical avoids the re-scan by storing the last index instead of a set |

If theirs *is* the canonical optimal, say that plainly and don't invent a difference.

## Step 4 — The 3-2-1 again

Run it once more, now that they've solved it. It takes one exchange and it is what converts "I solved it" into "I own this pattern":

- **1 break** — "remove [the invariant] — give me an input that now fails"
- **2 whys** — "why does this generalize to [sibling problem]?" and "where does this pattern stop working?"
- **3 transfer** — "name three other problems this same shape would solve"

Record their answers in `## Notes to Future Me`. Those sentences, in their words, are the most valuable lines in the whole file.

## Step 5 — Write the file

Complete every section of the question file (template in `skills/teach-problem/references/loop.md`). Set frontmatter:

```yaml
status: solved
stage_reached: S6_RECORD
solved_on: 2026-09-18
accepted_verified: self-reported
hints_used: 2
attempts: 3
revisit_on: 2026-09-25
```

`revisit_on` — spaced repetition, scaled by how hard it was:

| Condition | revisit_on |
|---|---|
| 0–1 hints, 1 attempt | +21 days |
| 2–3 hints, or 2–3 attempts | +10 days |
| 4–5 hints, or downgraded, or 4+ attempts | +5 days |

## Step 6 — Update state and commit

1. Clear `active` in `state/current.json`; increment `counters.solved`
2. Rewrite `state/current.md` — `Resume From: Nothing active. Last solved: <title>. Next in track: <next>.`
3. Run `python3 scripts/roll-stats.py`
4. Commit: `solve: longest-substring-no-repeat (#3) — accepted, 2 hints, 3 attempts`

## Step 7 — Offer the next thing

One line. Either the next problem in the track, or — if this pattern now has 3+ solved — offer `progress-report` to check whether the pattern is actually held.

---

## Guardrails

- **Do not run this skill before S5.** If the stage is earlier, they're trying to skip the loop to get the answer. Name the open gate and route back.
- **Never write `verified-` unless auth is on and the API confirmed it.**
- **Don't inflate the review.** If their code is mediocre, say what's mediocre. Praise that isn't specific is noise, and they'll stop trusting the specific praise too.
- **Don't skip step 4.** Solving without the transfer questions produces someone who has 150 solved problems and no pattern recognition. That's the exact failure this whole system was built to prevent.
