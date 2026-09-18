# Two modes, one repository

This repo is both an open-source tool and your private learning record. Those must not mix.

| | Framework mode | Personal mode |
|---|---|---|
| Branch | `main` | `personal-main` |
| Remote | `origin` (public) | `personal` (private) |
| You are | improving the tool | learning DSA |
| Contains | skills, scripts, curriculum, pattern briefs, visuals | all of that **plus** your profile, progress and notes |

**`PERSONALIZE` in `.env` decides the mode.** The working tree always stays on `main`; `personal-main` is worktree-only and written solely by `scripts/sync-vault.sh`.

**Identity and SSH are local, never global.** The global git config on this machine is a client account, and plain `git@github.com` is denied — only `git@github-lets-dsa:...` authenticates. Both are set up by `init-personal` and documented in `.claude/CLAUDE.md` (gitignored).

---

## What counts as personal

Listed in `.githooks/personal-paths`, and that file is what the guards read:

```
config/user.json      your level, targets, timeline
questions/            every problem you worked, in your words
topics/               your foundation notes
state/current.*       where you are right now
state/stats.json      your mastery numbers
curriculum/track.md   your personalized ordering
.env                  never tracked on any branch — may hold your LeetCode cookie
```

**Public, deliberately:** `patterns/*.md` and `visuals/*.html`. A brief about sliding windows and an animation of a heap sift are about the *pattern*, not about you — they're what makes the open-source repo worth cloning. Anything specific to your mistakes goes in your question files instead, which are private.

---

## Getting started

### Just learning

```bash
python3 scripts/dsa-git.py init-personal --remote git@github.com:you/lets-dsa-private.git
```

Create the private repo empty first. This creates `personal-main`, wires `personal` as its remote, starts tracking your data, and sets `MODE=personal`.

Then stay on that branch. `git push` goes to your private repo and nowhere else.

### Just contributing

Do nothing. A fresh clone is on `main` in framework mode, and no personal data exists.

### Both

You do both from the same tree, because the tree never switches branches.

- **Learning** writes gitignored files in place. Back them up with the vault script.
- **Framework work** is committed on `main` and pushed to `origin`.

```bash
# learning data -> private repo (the ONLY correct path to `personal`)
bash scripts/sync-vault.sh -m "solve: two-sum (#1) — accepted, 0 hints"

# framework -> public repo
git push origin main
```

### Why the vault script and not `git push personal main`

`personal:main` is fed by the `personal-main` branch inside `.personal-worktree`, which carries
data commits that local `main` does not have. The histories legitimately diverge, so a direct
push either fails as non-fast-forward or — with `--force` — destroys your backup. The script
merges `main` into `personal-main`, copies the personal files in, force-adds them, and pushes
`personal-main:main`.

### Pulling framework updates into the vault

Automatic — `sync-vault.sh` merges `main` first on every run.

Merges `main` into `personal-main`. Your data can't conflict, because `main` has never had a commit touching it.

---

## The guards

Installed by `init-personal` as `core.hooksPath=.githooks`. Three layers, because one is not enough:

| Layer | Stops |
|---|---|
| `.gitignore` | `git add` on a personal path while on `main` |
| `pre-commit` | `git add -f` followed by a commit on `main` |
| `pre-push` | pushing `personal-main` to `origin`, or any commit range containing personal paths |

`pre-push` is the one that matters. It runs even if the first two were bypassed, and it inspects the actual commit range rather than the working tree.

Verify at any time:

```bash
python3 scripts/dsa-git.py check
```

It fails loudly if any personal path has been committed on `main`.

### Bypassing

`--no-verify` skips the hooks. It exists because sometimes a guard is wrong. **A leak cannot be undone** — a pushed commit is public even after a force-push, because it has been cloned, cached and indexed. Read what the hook printed before you reach for it.

---

## Honest limits

- **Hooks are local.** They live in the clone. A fresh clone has no guards until `init-personal` sets `core.hooksPath`, and someone who clones your public repo isn't protected by yours.
- **`--no-verify` really does bypass them.** These guards stop accidents, not intent.
- **Nothing here scrubs history.** If personal data has already been pushed to `origin`, `check` will tell you, but removing it means rewriting history and treating anything exposed as already public.
- **`.env` is never tracked anywhere.** If you enable the LeetCode session cookie, it lives only on your disk.
