# Skills catalogue

Nine skills at `skills/<name>/SKILL.md`. Claude reads all of them at session start.

---

### `setup`
**Trigger:** `setup`, first run, or any failing Setup Gate
**Does:** six verified phases — environment, MCP check, interview, `config/user.json`, curriculum build, state init
**Writes:** `config/user.json`, `curriculum/track.md`, `state/*`
**Scripts:** `build-curriculum.py --verify`, `roll-stats.py`

### `dsa-command-center`
**Trigger:** `status`, `help`, `what now`, or an unclear first message
**Does:** routing only. Resumes an active problem instead of offering a menu
**Writes:** nothing

### `teach-problem`
**Trigger:** `teach X`, `how do I solve`, `hint`, `stuck`, a LeetCode URL
**Does:** the 7-stage gated loop S0→S6, the 5-rung hint ladder, the four-utterance S4 rule
**Writes:** `questions/**`, `state/current.*`
**Reference:** `references/loop.md` — full stage spec, gate scripts, question template
**Agents:** `problem-scaffolder`, `explainer-drafter`, `dry-run-generator`

### `record-solve`
**Trigger:** `solved`, `accepted`, pasting code after S5
**Does:** stage S6 — code review, canonical optimal, complexity comparison, transfer questions, spaced-repetition scheduling
**Writes:** `questions/**`, `state/*`
**Note:** the only skill permitted to write solution code, and only after acceptance
**Agents:** `submission-grader`

### `daily-drill`
**Trigger:** `today`, `next`, `what should I do`
**Does:** picks the day's set — revisits first, then parked, then track. Enforces the difficulty ramp
**Writes:** nothing

### `pattern-brief`
**Trigger:** `explain <pattern>`, `I keep confusing X and Y`
**Does:** teaches a pattern in the abstract; writes `patterns/<slug>.md`
**Agents:** `pattern-researcher`

### `visual-explainer`
**Trigger:** `visualize`, `show me`, `I can't picture it`
**Does:** inline sketch now + a saved self-contained animated HTML file
**Writes:** `visuals/<pattern>/*.html`
**Agents:** `visual-builder`

### `interview-mode`
**Trigger:** `interview me`, `mock interview`
**Does:** timed in-persona interview, one nudge maximum, escalating follow-up, scored rubric
**Writes:** `questions/**` with `mode: interview`

### `progress-report`
**Trigger:** `progress`, `am I ready`
**Does:** mastery bands per pattern, largest gap by blast radius, honest readiness verdict
**Writes:** nothing (regenerates `state/stats.json` via script)
**Scripts:** `roll-stats.py`

---

## Agents

`.claude/agents/` — non-interactive work only. Subagents cannot hold a dialogue, so the teaching loop cannot live in one. Each writes its own file and returns a path plus a short summary.

| Agent | Model | Returns |
|---|---|---|
| `visual-builder` | sonnet | path to the HTML |
| `pattern-researcher` | sonnet | path to the brief |
| `dry-run-generator` | sonnet | input + expected trace (small, inline) |
| `submission-grader` | sonnet | review (inline, ≤40 lines) |
| `explainer-drafter` | sonnet | draft prose (inline, <250 words) |
| `problem-scaffolder` | haiku | path to the scaffold |
| `stats-roller` | haiku | four lines of counts |

`dry-run-generator` is Sonnet rather than Haiku on purpose: a wrong expected trace makes the tutor mark a correct answer wrong and teaches the learner something false.

## Scripts

| Script | Does | Writes |
|---|---|---|
| `build-curriculum.py [--verify] [--refresh]` | fetches NeetCode 150, maps to the 20-pattern taxonomy, verifies every slug against LeetCode's public GraphQL | `curriculum/merged.json` |
| `roll-stats.py` | aggregates question frontmatter into mastery bands | `state/stats.json` |
| `status.py` | read-only session-start snapshot, reports failing setup gates | nothing |

One writer per file. `roll-stats.py` is the only thing that writes `state/stats.json`; `teach-problem` is the only thing that writes `state/current.*`.
