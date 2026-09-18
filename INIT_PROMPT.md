# First message

Paste one of these as your **first message** after opening lets-dsa in Claude.

---

## If you're here to learn DSA

> I've just cloned lets-dsa and I want to learn. Read `CLAUDE.md`, then `.claude/CLAUDE.md`
> if it exists, then every `skills/*/SKILL.md`. Then run `skills/setup` with me.
>
> Work one phase at a time and verify each before moving on. Tell me what actually worked
> rather than assuming — if the LeetCode MCP doesn't connect, say so plainly instead of
> reporting success you haven't checked.
>
> Ask me, don't guess: my level, my target companies, my timeline, how much time I really
> have per day, and which language I'll submit in.
>
> Set me up in **personal mode** — my progress and notes go to my own private repo, never
> to the public one. Walk me through pointing `PRIVATE_REPO_URL` at it.
>
> Two things I want you to hold to for the whole project:
>
> 1. **Never give me solution code before I've submitted an accepted answer on LeetCode.**
>    Not when I ask nicely, not when I'm frustrated, not "just the key line", not as
>    pseudocode with the syntax removed. Use the five-rung hint ladder, then refuse. I'm
>    going to push, and I want you to hold.
> 2. **Never advance a stage because I said "got it".** Make me produce something — a
>    trace, a complexity figure, a breaking input.
>
> Start me at the beginning: foundations first, then the first pattern's brief, then my
> first problem.

## If you're here to work on the tool

> I've cloned lets-dsa and I want to work on the framework, not learn from it. Read
> `CLAUDE.md` and `docs/MODES.md`. Confirm I'm in **framework mode** (`PERSONALIZE=false`,
> branch `main`) and don't create any personal files. Then tell me what you'd improve.

---

## What setup actually does

Six verified phases: environment check → LeetCode MCP connection test → interview you →
write `config/user.json` → build the curriculum, foundations and ladder → initialize state.

It runs four scripts and reports their real output:

| Script | Produces |
|---|---|
| `build-curriculum.py --verify` | 343 problems from 7 curated sheets, every slug verified against LeetCode |
| `build-foundations.py` | 8 prerequisite topics, ~16 hours, 61 free article/video links |
| `build-track.py` | `curriculum/track.md` — your ladder: 6 tiers, with floor / interview-ready / strong targets |
| `roll-stats.py` | your (empty) mastery stats |

## How the learning is shaped

**Levels** — `beginner` / `intermediate` / `advanced`, set at setup, overridable per problem
("explain this like I'm a beginner"). It changes pace and vocabulary. **It never changes the
gates** — a beginner gets more analogy, not an easier dry-run.

**Foundations before problems** — 8 topics. `01-complexity-analysis` gates every pattern;
`05-basic-recursion` gates five. You can push past a gate; the override is recorded so your
progress report stays honest.

**Theory before each pattern** — a written brief in `patterns/`: how to recognize it, the
invariant, the named algorithms, a traced micro-example. About five minutes. Orientation,
not a test.

**Then the loop, per problem** — S0 select · S1 pattern · S2 intuition (you trace an input
Claude gives you) · S3 brute→better→optimal · S4 your pseudocode critiqued · S5 you solve on
LeetCode · S6 review and record.

**Targets** — floor **90** (every pattern met once, *not* ready), interview-ready **180**,
strong **250**. Weighted by what the curated sheets actually invest in, not spread evenly.
A count alone never means ready: 180 solved at hint rung 5 is worse than 120 solved cold.

## Commands

| Type | Gets you |
|---|---|
| `setup` | first-run onboarding |
| `basics` | the 8 foundation topics |
| `today` | today's problems, sized to your real budget |
| `next` | next problem in your track |
| `pattern <name>` | the theory brief for a pattern |
| `hint` | one rung up the ladder — costs a rung, they don't reset |
| `park` | save exactly where you are |
| `downgrade` | an easier problem in the same pattern, fully worked |
| `solved` | review, canonical optimal, complexity comparison |
| `visualize <thing>` | animated explanation, saved to `visuals/` |
| `interview` | mock interview, in persona, with an honest scorecard |
| `progress` | mastery per pattern and a readiness verdict |
| `status` | where am I right now |

## Your data

In personal mode, everything about you — profile, progress, notes, solved problems — is
gitignored from the public branch and backed up to your private repo:

```bash
bash scripts/sync-vault.sh -m "solve: two-sum (#1) — accepted, 0 hints"
```

Three git hooks block a leak to the public remote, including if you rename the branch.
Check any time with `python3 scripts/dsa-git.py check`. Full detail in `docs/MODES.md`.

Commits use a **local** git identity, never your global one — see `.claude/CLAUDE.md`.
