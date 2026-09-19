# Contributing to lets-dsa

Thanks for wanting to. This project has one unusual constraint, and almost every rule below follows from it.

> **The tutor must never hand over a solution before the learner has earned it.**

A contribution that makes it easier to leak an answer is a regression, however useful it looks.

---

## Before you start

```bash
git clone https://github.com/shubhamcodess/lets-dsa.git
cd lets-dsa
```

Then set framework mode, so nothing personal is created:

```bash
echo "PERSONALIZE=false" > .env
```

Confirm you're clean:

```bash
python3 scripts/dsa-git.py check
```

In framework mode Claude will refuse to write `questions/`, `topics/`, `state/current.*` or `config/user.json` — that's deliberate, not a bug.

---

## What to work on

| Good contributions | Why |
|---|---|
| **`ListNode` / `TreeNode` harnesses for `oa-run.py`** | Unlocks ~67 problems currently refused. Well-defined: LeetCode's array-to-list and level-order-to-tree formats, 4 languages. |
| **A new curated sheet** | Add a fetcher to `scripts/build-curriculum.py`. It must merge by LeetCode slug and verify every slug. |
| **Pattern brief improvements** | `patterns/*.md`. Especially "how to recognize it" and "confusable with" — the two sections that carry the value. |
| **Saved animations** | `visuals/<pattern>/*.html`. Self-contained, no CDN, must show the invariant breaking and being restored. |
| **FSRS parameter fitting** | `schedule.py fit` deliberately refuses today. Implement it once there's a real review corpus to fit against. |
| **Design-problem harness** | LRU Cache style: constructor plus an operation sequence. A different harness shape entirely. |

Please open an issue before large work. A skill rewrite touches the guardrail and is worth discussing first.

---

## Hard rules

### 1. Never weaken the guardrail

Do not add a way to reveal a solution early. That includes:

- an "unlock" phrase, a confidence threshold, or an escape after N failures
- reading a linked editorial and relaying its contents (that's the solution with a citation attached)
- relaying LeetCode's own `hints` array before S5 — those are frequently the invariant stated outright
- removing any of the four denied MCP tools from `.claude/settings.json`

The hint ladder has five rungs and then a refusal. That's the complete set of responses to pressure. If you think a sixth rung is needed, open an issue and argue for it.

### 2. Never put a learner's data in a public path

`patterns/**` and `visuals/**` are public. They must contain nothing about any specific learner — no stats, no identity, no "you usually get this wrong". Personal traps belong in `questions/`, which is private.

### 3. Verify, don't assert

This repo has a strong bias toward checking. Several bugs in it were found only because output was verified instead of trusted:

- `git add -f a b c` is atomic — one missing path silently staged nothing
- a `pre-push` hook blocked the *cleanup* of a leak, because it flagged deletions
- compile errors pointed into a generated harness, telling learners they wrote lines they hadn't

So: run the thing, read the real output, and put the numbers in the PR.

### 4. Don't fabricate data

Every problem in `curriculum/merged.json` is verified against LeetCode's public GraphQL. Every pattern assignment carries a `pattern_source` saying how it was decided. Company tags carry their source URL, and an empty list means *not searched* — which the data says explicitly.

If you can't source it, leave it empty and say so. An honest gap beats a confident guess.

### 5. Regenerate, don't hand-patch

`curriculum/merged.json`, `curriculum/track.md`, `config/foundations.json` and `state/stats.json` are **generated**. Hand-editing them works until the next rebuild erases it — which has already happened once in this project's history, losing a whole research layer.

If a transformation needs to survive, put it in a script:

```bash
python3 scripts/build-curriculum.py --verify   # then:
python3 scripts/apply-research.py
python3 scripts/build-foundations.py
python3 scripts/build-track.py
python3 scripts/roll-stats.py
```

---

## Writing a skill

Skills live at `skills/<name>/SKILL.md` with **exactly two** frontmatter keys:

```yaml
---
name: my-skill
description: >
  What it does. Triggers on: "literal phrase", "another phrase", ...
---
```

They must perform reliably on Sonnet and Haiku, not just Opus. That means:

- literal output templates with a filled example
- bounded step counts ("3–6 steps", "exactly 4 rounds")
- decision tables with an explicit `| anything else | ask |` row
- one condition per row — never "if stuck and untraced and rung 3+"
- closed vocabularies for every label
- verbatim refusal scripts, not "decline politely"
- a pre-send self-check at the end
- the hard constraint stated at **both** the top and the bottom — middle-of-file instructions decay fastest

## Writing a subagent

`.claude/agents/*.md` needs `name`, `description`, `model`, `tools`. Note the convention differs from skills — that's intentional.

Agents **write their own files and return a path plus ≤5 lines.** A subagent's return value lands in the expensive main context, so returning 600 lines of generated HTML saves nothing.

Pick the model honestly. `dry-run-generator` is Sonnet rather than Haiku because a wrong expected trace makes the tutor mark a correct answer wrong and teaches the learner something false.

---

## Commits and PRs

Prefix from this closed vocabulary:

```
stage:  solve:  hint:  visual:  pattern:  park:  downgrade:
curriculum:  stats:  setup:  topic:  docs:  fix:  feat:
```

Never `git add -A` blindly — stage what you wrote.

A good PR body says **what you verified and how**, with the real output. "Tested on two-sum in all four languages, 3/3 each" is worth more than "should work".

If your change touches the guardrail in any way, say so explicitly at the top of the PR. That gets read carefully, not rejected.

---

## Running the checks

```bash
python3 scripts/status.py                  # setup gates
python3 scripts/dsa-git.py check           # no personal data on the public branch
python3 scripts/oa-run.py --slug two-sum --lang java --file <sol>.java --tests <t>.json
```

There is no test suite yet. Adding one is itself a welcome contribution — start with `oa-run.py`'s type mapping and `schedule.py`'s interval maths, which are the two places pure functions make it easy.

---

## A note on tone

The tutor is allowed to be blunt. "Not ready" is a real answer; so is "you break invariants and you under-explain". What it is never allowed to be is *encouraging in a way that isn't true* — a soft progress report costs someone a real interview.

Keep that voice in anything you write for it.
