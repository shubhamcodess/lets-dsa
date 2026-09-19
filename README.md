<div align="center">

# lets-dsa

### A DSA tutor that refuses to give you the answer.

**343 verified problems** · **20 patterns** · **8 foundation topics** · **4 languages**

Built on Claude Code. Learn the pattern, derive the approach, solve it on LeetCode yourself.

</div>

---

## What this is

There's no shortage of DSA material — NeetCode 150, Striver's A2Z, Blind 75 are all good.

What's missing is everything around them. None of them knows whether you understood the last problem. So the same thing happens to everyone: you clear a run of Easies, hit a Medium that assumes a jump you never made, and fall off. You've *done* sixty problems and can't solve a new one.

This is the missing layer — **sequencing**, **pattern recognition**, and **proof you actually understood**. That last one is the hard part, because nodding is free.

> ### The bet
>
> **Claude never writes the solution before you've solved it.**
>
> Not when you ask nicely. Not when you're frustrated. Not "just the key line", not as pseudocode with the semicolons removed.
>
> You get five hints, each more specific, then it refuses — and offers a real way out: it fully solves an *easier* problem in the same pattern, then sends you back to this one.

Reading a solution feels like learning and isn't. The person who reads the answer to Longest Substring can't solve Minimum Window next week. The person who derived it can.

**This is enforced, not promised.** Four MCP tools that could fetch or submit a solution are denied at the project level — Claude *cannot* look it up.

---

## Quick start

### 1. Get Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Claude Code needs a model behind it. Two ways:

| | |
|---|---|
| **Claude subscription** *(recommended)* | Pro is enough — [claude.com/pricing](https://www.claude.com/pricing) |
| **Local models via Ollama** *(free)* | [Claude Desktop + Ollama](https://docs.ollama.com/integrations/claude-desktop) · macOS |

> **Honest note on local models.** Two things to know before you rely on it.
>
> Ollama's guide covers **Claude Desktop**. This project runs in Claude Code, and the docs don't state whether the Code tab picks up the local model — check that before committing to it.
>
> And the harder problem: this project's whole value is the tutor *refusing* under pressure, holding a seven-stage state machine, and following long instruction files exactly. Small local models tend to leak the answer when you push. It will run — it may not hold the line.

### 2. Clone this repo

```bash
git clone https://github.com/shubhamcodess/lets-dsa.git
cd lets-dsa
```

### 3. Pick why you're here

| | Learning DSA | Improving the framework |
|---|---|---|
| **`.env`** | `PERSONALIZE=true` | `PERSONALIZE=false` |
| **Your data** | goes to a private repo of your own | none is created |
| **Setup** | step 4 | `echo "PERSONALIZE=false" > .env`, then skip to step 5 |

### 4. Learning? Point it at a private repo

Your progress and notes must never land in a public repo. Create an **empty private repository** on GitHub, then:

```bash
python3 scripts/dsa-git.py init-personal --remote git@github.com:YOU/lets-dsa-private.git
```

That writes `.env`, adds your private remote, and installs three git hooks that block a leak. It pushes nothing.

### 5. Start

```bash
claude
```

Paste [`INIT_PROMPT.md`](INIT_PROMPT.md) as your first message, then type `basics`.

<details>
<summary><b>Verify and back up</b></summary>

```bash
python3 scripts/dsa-git.py status    # mode, remotes, identity, what's protected
python3 scripts/dsa-git.py check     # fails loudly if anything personal is on the public branch
bash scripts/sync-vault.sh -m "solve: two-sum (#1) — accepted, 0 hints"
```

Using a different GitHub account than your machine default? Pass `--name` and `--email` to `init-personal` — it sets an identity for this repo only and leaves your global config alone.

**Optional, for `oa` mode:** `javac`, `clang++` or `node`, depending on the language you want to write in. Python works out of the box.

</details>

---

## How a problem goes

Seven stages. You can't skip one, and **nothing advances because you said "got it"** — only a produced artifact passes a gate.

| Stage | What happens | You move on when |
|---|---|---|
| **S0 · Select** | Claude picks the next problem from your ladder and fetches it live from LeetCode — statement, constraints, examples. A file is created for it. | automatic |
| **S1 · Pattern** | You're taught the *family*, not this problem. What sliding window is, how to spot one, two siblings you've already seen. | you name the pattern **and** the signal in *these constraints* that selects it — in your own words |
| **S2 · Intuition** | The real work. Claude asks questions until you find the invariant yourself — the thing that stays true, that the whole algorithm exists to maintain. | Claude hands you six characters and asks for the state after each step. You trace it correctly. |
| **S3 · Ladder** | You propose brute force, then better, then optimal — in that order, before Claude reacts to any of them. | you give time and space for all three, plus one sentence on what optimal buys that better doesn't |
| **S4 · Pseudocode** | You write the algorithm in English. Claude may only quote your own lines, label a defect, give a counterexample, or ask a question. It cannot write a corrected line. | your algorithm survives an adversarial input Claude picks |
| **S5 · Submit** | Claude stops teaching and hands you a card that **opens the problem on LeetCode**. You write and submit it there — that's where the real verdict comes from. | you come back with an accepted submission |
| **S6 · Record** | The guardrail lifts. Your code is reviewed, the canonical optimal shown, complexities compared, everything written to your problem file. | — |

**S2 does the most work.** Six characters and "what's the state after each step" can't be passed by nodding — it's the cheapest way to find out whether an explanation landed.

**Stuck is a supported state.** Fail the S2 trace three times and Claude *downgrades*: it fully solves an easier problem in the same pattern, front to back, then returns you to S2 on the original. Or `park` it and keep your exact place, hint count included.

**Every problem ends on leetcode.com.** S5 hands you a direct link and gets out of the way. Want to practise the *conditions* first? `oa` gives you a bare editor — no autocomplete, no highlighting — compiled and run for real.

---

## What you get

| | |
|---|---|
| **Foundations first** | 8 prerequisite topics, ~16 hours, **61 free article and video links**. Complexity analysis gates *all twenty* patterns; recursion gates five. |
| **Theory per pattern** | A written brief for each: how to recognize it from a problem *statement*, the invariant, **30 named algorithms** (Dijkstra, Kadane, Boyer–Moore, KMP, Sieve…), a traced micro-example, where it breaks. |
| **A ladder that can't skip** | Patterns topologically sorted into 6 tiers — none appears before its prerequisites. Inside a pattern: Easy → Medium → Hard, highest-consensus problem first. |
| **Real code, no IDE** | `oa` opens a bare editor and actually compiles and runs your code in Java, C++, TypeScript or Python. Nothing is checked while you type — the editor holds no compiler. |
| **Spaced repetition** | Intervals come from hints and attempts, never self-report. Clean recall grows 5→8→12→19→29 days; a lapse collapses to within a week. |
| **Your own error profile** | Built from your defect tables and the patterns you misname. *"You've called sliding-window problems two-pointers four times."* No general tool can know that. |
| **Graded explanation** | Narration is scored at every stage on precision, cost-awareness and tradeoff. Solving silently is how strong coders fail interviews. |
| **Mock interviews** | Timed, in persona, escalating follow-ups, scored rubric — and a readiness answer that's allowed to be *no*. |

### Readiness is three numbers, not one

| Target | Problems | Means |
|---|---|---|
| Floor | **90** | You've met every pattern once. **Not interview-ready.** |
| Interview-ready | **180** | Realistic for product-based, weighted by what curators actually invest in |
| Strong | **250** | Comfortable rather than surviving |

### Beginners get worked examples

Problem 1 in a new pattern is fully worked by Claude, problem 2 partially, problem 3 onward pure Socratic — per pattern, fading automatically. Novices retain 20–40% more this way, and it reverses with expertise, so at intermediate and advanced it never happens.

---

## What accumulates

```
questions/03-sliding-window/longest-substring-without-repeating-characters.md
```

One file per problem, organized by **pattern** rather than topic — so browsing the tree is itself revision.

Each holds the problem, the signal *in your words*, the invariant *in your words*, your ladder, your pseudocode, the defects found in it, your accepted code, the canonical optimal, and a note to your future self.

After a few months that folder is your own pattern library. That's the actual output — the solved count is a side effect.

---

## Commands

| | |
|---|---|
| `basics` | the 8 foundation topics |
| `today` · `next` | today's problems, sized to your budget · the next one in your track |
| `pattern <name>` | the theory brief |
| `hint` | one rung up the ladder — costs a rung, they don't reset |
| `park` · `downgrade` | save your place · an easier problem in the same pattern, fully worked |
| `solved` | review, canonical optimal, complexity comparison |
| `oa <problem>` | bare editor, real compile and run, verdict only at submit |
| `visualize <thing>` | animated explanation, saved to `visuals/` |
| `interview` | mock interview with an honest scorecard |
| `progress` | mastery per pattern and a readiness verdict |

---

## Your data stays yours

Progress, notes and profile are gitignored from the public branch and backed up to **your** private repo. Three layers, because `.gitignore` alone isn't enough:

| Layer | Stops |
|---|---|
| `.gitignore` | a normal `git add` of a personal path |
| `pre-commit` | `git add -f` followed by a commit on `main` |
| `pre-push` | pushing personal data to the public remote — **even on a renamed branch** |

Pattern briefs and animations stay public on purpose. A brief about sliding windows is about the pattern, not about you — and it's what makes this repo worth cloning.

Full detail and the honest limits: [`docs/MODES.md`](docs/MODES.md)

---

## Where the content comes from

Seven curated sheets, merged by LeetCode slug into **343 unique problems** — 73 Easy · 209 Medium · 61 Hard.

| Source | Problems | On LeetCode |
|---|---|---|
| [NeetCode 150](https://neetcode.io/) | 150 | 150 |
| [Striver's A2Z](https://takeuforward.org/dsa/strivers-a2z-sheet-learn-dsa-a-to-z) | 474 | 243 |
| [Striver's SDE](https://takeuforward.org/dsa/strivers-sde-sheet-top-coding-interview-problems) | 191 | 118 |
| [Blind 75](https://takeuforward.org/dsa/blind-75-leetcode-problems-detailed-video-solutions) | 75 | 66 |
| [Striver's 79](https://takeuforward.org/dsa/strivers-79-last-moment-dsa-sheet-ace-interviews) | 79 | 55 |
| [CodingShuttle CS SDE](https://www.codingshuttle.com/sheets/cs-sde-sheet/) | 169 | 169 |
| [LeetCode "Striver SDE" list](https://leetcode.com/problem-list/eeudwo2i/) | 117 | 117 |

Every slug is verified against LeetCode's public GraphQL. Live problem data comes through a pinned [MCP server](https://github.com/jinzcdev/leetcode-mcp-server).

**Sitting in several sheets is the signal.** No honest public source gives per-problem company tags, but a problem in Blind 75 *and* Striver's 79 *and* NeetCode 150 is one three independent curators thought worth your time. That drives ordering — not invented labels.

**308 problems live on GeeksforGeeks or Coding Ninjas.** They can't run the loop, which ends in a LeetCode submission, so they're kept separately with their ordering and free article links rather than discarded.

---

## Honest limitations

- **Claude can't verify you got Accepted.** Auth is off by default, so "solved" is what you say it is. Turn on `LEETCODE_SESSION` and it becomes a real check.
- **Company tags cover 42 of 343**, from third-party research, each with its source URL. An empty list means *not searched*, not *nobody asks it* — and the data says so.
- **`oa` can't harness every problem.** Design problems and `ListNode`/`TreeNode` are refused explicitly rather than mis-harnessed.
- **The no-code rule is prompt-enforced.** What's mechanical is the MCP deny list, which stops Claude fetching a solution at all.
- **19 problems are LeetCode Premium.** Setup offers free substitutes.

---

## Under the hood

**11 skills · 7 subagents · 11 scripts.** Every file is markdown or JSON. Every change is git-committed. Nothing lives in a black box — including your progress, which is plain text you can read without this tool.

Nothing per-problem is pre-generated: the repo holds the index, and statements, briefs, harnesses and visuals are constructed when you ask for them.

Defaults to Sonnet — this is text-heavy teaching, not hard reasoning, and it costs a fraction of Opus to run.

[`CLAUDE.md`](CLAUDE.md) is the operating manual · [`docs/SKILLS.md`](docs/SKILLS.md) covers each skill · [`docs/MODES.md`](docs/MODES.md) covers privacy

---

## Contributing

Wanted — especially `ListNode`/`TreeNode` harnesses for `oa` mode, which unlock ~67 currently-refused problems.

One rule above all others: **never make it easier to leak a solution.**

See [`CONTRIBUTING.md`](CONTRIBUTING.md)
