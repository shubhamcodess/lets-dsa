# Git behaviour — full detail

The rules that can cause harm if missed are summarised in `CLAUDE.md`. This is the rest.


### Identity — check it before the first commit

**Never assume the global git config is the right account for this repo.** On many machines it belongs to a work or client account, and a commit that falls back to it is attributed to the wrong person.

```bash
git config --local user.email    # is this the account that should own these commits?
```

If it is empty and the global identity is wrong for this repo, set a local one:

```bash
git config --local user.name "Your Name"
git config --local user.email "you@example.com"
```

Never run `git config --global` anything — that changes the identity for every repo on the machine.

**Machine-specific identity, SSH aliases and remote URLs belong in `.claude/CLAUDE.md`**, which is gitignored. If that file exists it is authoritative and overrides anything here.

### Remotes

| Remote | Holds | Branch |
|---|---|---|
| `origin` | framework only — public | `main` |
| `personal` | framework + learning data — **private** | `main`, fed from `personal-main` |

Set up with `python3 scripts/dsa-git.py init-personal --remote <your private repo>`. If this machine needs an SSH host alias to reach the right account, `.claude/CLAUDE.md` records it.

### Committing

Every write is followed by a commit, with a prefix from the closed vocabulary:
`stage:` `solve:` `hint:` `visual:` `pattern:` `park:` `downgrade:` `curriculum:` `stats:` `setup:` `topic:` `docs:`

Never `git add -A` blindly — stage the specific files you wrote.

### After every framework commit

Skills, scripts, docs, `config/patterns.json`, `config/foundations.json`, curriculum data, `patterns/**`, `visuals/**`:

```bash
git push origin main
bash scripts/sync-vault.sh -m "[what changed]"
```

### After every learning update

A solved problem, a foundation topic, a stage transition worth keeping:

```bash
bash scripts/sync-vault.sh -m "solve: longest-substring-no-repeat (#3) — accepted, 2 hints"
```

**Always pass a meaningful `-m`.** Never let it fall back to the timestamp default — six months from now that log is the only record of what happened.

### Never do these

- **Never `git push personal main` from the local `main` branch.** `personal:main` is fed by `personal-main` in `.personal-worktree`, which has learning-data commits `main` does not. A direct push fails as non-fast-forward, or with `--force` destroys the backup. `scripts/sync-vault.sh` is the only correct path to `personal`.
- **Never check out `personal-main` in the main working tree.** It is worktree-only. Switching to it and back would delete the learner's notes from disk.
- **Never commit personal data on `main`.** Three hooks in `.githooks/` will block it, but they are a safety net, not a plan.
- **Never push on the learner's behalf without saying so.** Commit, run the vault sync when data changed, and tell them what went where.

If `git push origin main` is rejected as non-fast-forward after a history rewrite, force push is safe and expected — `origin` only ever holds framework files:

```bash
git push origin main --force
```


---

## Repository structure

```
lets-dsa/
├── CLAUDE.md                   ← this file — read first, always
├── README.md                   ← philosophy, quick start
├── INIT_PROMPT.md              ← the message a new user pastes first
├── .claude/
│   ├── settings.json           ← model: sonnet + the MCP deny list (the hard guardrail)
│   └── agents/                 ← 7 subagents, non-interactive work only
├── .mcp.json               ← leetcode MCP, version-pinned
├── config/
│   ├── user.json               ← level, targets, timeline, budget  (gitignored)
│   └── patterns.json           ← the 20-pattern taxonomy — signals, siblings, deps
├── curriculum/
│   ├── sources/                ← raw fetched lists
│   ├── merged.json             ← every problem, with list memberships + tags
│   └── track.md                ← THEIR ordered path
├── patterns/<slug>.md          ← 20 pattern briefs
├── questions/<NN>-<pattern>/<problem>.md   ← the permanent record — one file per problem
├── visuals/<NN>-<pattern>/<name>.html      ← saved animated explainers
├── state/
│   ├── current.json            ← AUTHORITATIVE pointer
│   ├── current.md              ← human mirror, carries `Resume From:`
│   └── stats.json              ← mastery per pattern
├── skills/                     ← 9 skills, read them all at session start
└── scripts/                    ← build-curriculum.py, roll-stats.py, status.py
```

---
