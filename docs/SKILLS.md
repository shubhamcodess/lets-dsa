# Skills catalogue

Nine skills at `skills/<name>/SKILL.md`. Claude reads all of them at session start.

---

### `setup`
**Trigger:** `setup`, first run, or any failing Setup Gate
**Does:** six verified phases — environment, MCP check, interview, `config/user.json`, curriculum build, state init
**Writes:** `config/user.json`, `curriculum/track.md`, `state/*`
**Scripts:** `build-curriculum.py --verify`, `roll-stats.py`

### `foundations`
**Trigger:** `basics`, `where do I start`, `explain big O`, or any failing foundation gate
**Does:** teaches the 8 prerequisite topics; comprehension check per topic; gate enforcement
**Writes:** `topics/<id>.md`
**Note:** the no-code guardrail does NOT apply here — explaining recursion with code is the point
**Scripts:** `build-foundations.py`

### `dsa-command-center`
**Trigger:** `status`, `help`, `what now`, or an unclear first message
**Does:** routing only. Resumes an active problem instead of offering a menu
**Writes:** nothing

### `teach-problem`
**Trigger:** `teach X`, `how do I solve`, `hint`, `stuck`, a LeetCode URL
**Does:** the 7-stage gated loop S0→S6, the 5-rung hint ladder, the four-utterance S4 rule
**Faded worked examples:** at `beginner` only, and per pattern — 0 solved → DEMONSTRATE (fully worked, including code), 1 → COMPLETE (English algorithm with `<you decide: …>` holes), 2+ → SOCRATIC. Recorded as `teach_mode`; a demonstrated problem never counts as solved
**Explain out loud:** narration required and graded at S1–S4 and S6 on precision / cost-awareness / tradeoff, recorded as `explanation`
**Confusion capture:** wrong pattern names at S1 go to `s1_wrong_guesses`, which feeds `confusion.py`
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
**Trigger:** `explain <pattern>`, `I keep confusing X and Y`, and automatically before the first problem in any pattern
**Does:** teaches a pattern in the abstract; owns `patterns/<slug>.md`
**State:** all 20 briefs are pre-written. The intro gate in `daily-drill` delivers the brief before a pattern's first problem — orientation, not a gate you can fail
**Agents:** `pattern-researcher` (regenerates or updates a brief)

### `visual-explainer`
**Trigger:** `visualize`, `show me`, `I can't picture it`
**Does:** inline sketch now + a saved self-contained animated HTML file
**Writes:** `visuals/<pattern>/*.html`
**Agents:** `visual-builder`

### `interview-mode`
**Trigger:** `interview me`, `mock interview`
**Does:** timed in-persona interview, one nudge maximum, escalating follow-up, scored rubric
**Writes:** `questions/**` with `mode: interview`

### `oa-practice`
**Trigger:** `oa`, `timed coding`, `let me actually code this`, or interview-mode's coding phase
**Does:** renders a bare in-chat editor (no highlighting, no autocomplete, no auto-indent, no feedback), then compiles and runs the submission against real tests
**Writes:** `state/oa-attempts.json` (gitignored, private)
**Scripts:** `oa-run.py`
**Languages:** java, cpp, typescript, python3. Refuses design problems and `ListNode`/`TreeNode` rather than mis-harnessing them

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
| `build-curriculum.py [--verify] [--refresh]` | fetches 5 curated sheets (NeetCode 150 + Striver A2Z / SDE / Blind 75 / Striver 79), merges them by LeetCode slug, verifies every slug against LeetCode's public GraphQL, and infers a pattern for anything NeetCode didn't already categorize | `curriculum/merged.json` |
| `build-foundations.py` | builds the 8 prerequisite topics and their gates from Striver A2Z steps 1–2 | `config/foundations.json` |
| `apply-research.py [--dry-run]` | merges model/web research into the curriculum, re-verifying every proposed pattern against real LeetCode tags and discarding any company list with no source URL | `curriculum/merged.json` |
| `sync-vault.sh -m "..."` | merges main into personal-main in `.personal-worktree`, copies learning data in, commits and pushes `personal-main:main` to the private repo. The only correct path to the `personal` remote | private repo |
| `dsa-git.py {status,init-personal,save,sync,check}` | dual-mode git: routes personal data to the private remote and framework work to the public one; installs and dry-runs the leak guards | git config, branches, worktree |
| `build-track.py` | materializes the ladder into `curriculum/track.md`: pattern tiers from the dependency graph, per-tier advancement counts with a required difficulty mix, and problems ordered by ramp then sheet consensus | `curriculum/track.md` |
| `schedule.py {grade,next,due}` | FSRS-inspired spaced repetition. Derives a grade from hints/attempts (never self-report), grows intervals 5→8→12→19→29d on clean recall, collapses to ≤7d on a lapse | question frontmatter `srs_*` |
| `confusion.py` | builds a personal error profile from the learner's own defect tables, wrong S1 pattern guesses and hint counts | `state/confusion.json` |
| `oa-run.py --slug S --lang L --file F [--tests T] [--record]` | fetches `metaData` live, generates a test harness for that problem, compiles and runs the learner's code, remaps compile-error line numbers to their own file, and appends the attempt to the ledger | `state/oa-attempts.json` |
| `roll-stats.py` | aggregates question + topic frontmatter into mastery bands and open foundation gates | `state/stats.json` |
| `status.py` | read-only session-start snapshot, reports failing setup gates | nothing |

One writer per file. `roll-stats.py` is the only thing that writes `state/stats.json`; `teach-problem` is the only thing that writes `state/current.*`.


## Curriculum data model

`curriculum/merged.json` (schema 2) has two collections.

**`problems`** — keyed by LeetCode slug. Every entry is verified; `verified: true` means the
id, title, difficulty and `topic_tags` came back from LeetCode's public GraphQL, not from a
guess. Notable fields:

| Field | Meaning |
|---|---|
| `lists` | which sheets contain it — `neetcode150`, `striver_a2z`, `striver_sde`, `blind75`, `striver79`. Membership in several is the best free proxy for interview frequency. |
| `pattern` / `pattern_source` | the assigned pattern and **how** it was assigned. `neetcode` = from the NeetCode category. `override` = hand-split into a finer pattern. `leetcode-tags:*` = inferred from real topic tags. `unassigned` = left null rather than guessed. |
| `striver` | `{step_no, step, substep}` from the A2Z sheet — the sequencing signal. |
| `resources` | free `article` and `youtube` links from takeuforward. Used for the refusal's editorial exit and for post-S6 review. **Never read and relayed during S1–S5.** |
| `companies` | always `[]`. LeetCode gates company tags behind Premium; fabricating them would poison the curriculum. |

**`non_leetcode`** — Striver problems hosted on GeeksforGeeks or Coding Ninjas rather than
LeetCode. They cannot run through the S0–S6 loop (which ends in a LeetCode submission), so
they are kept out of `problems` but not discarded: they carry step ordering and free article
and video links, which is real sequencing value.

`pattern_source` exists so a thin or odd-looking pattern assignment can be audited rather
than trusted. If a problem lands in the wrong folder, that field says which rule put it there.
