# lets-dsa

A DSA tutor that refuses to give you the answer.

---

## Why this exists

There is no shortage of DSA material. NeetCode 150, Striver's A2Z, Blind 75, the Grokking patterns — all good, all free or cheap, all better than anything you'd assemble yourself.

The shortage is in everything around them. Each has its own tone and its own pace. None of them knows whether you understood the last problem. So the same thing happens to almost everyone: you clear a run of Easies, feel fine, hit a Medium that assumes a jump you never made, and fall off. You have "done" sixty problems and can't solve a new one.

What's missing isn't content. It's **sequencing**, **pattern recognition**, and **proof that you actually understood** — and that last one is the hard part, because nodding is free.

This is that layer. It sits on top of the curated lists it doesn't try to replace.

## The bet

**Claude never writes the solution before you've solved it.**

Not when you ask nicely. Not when you're frustrated. Not "just the key line", not as pseudocode with the semicolons removed, not in a different language so it doesn't count.

You get five hints, each more specific than the last, and then it refuses — and offers you a real way out instead: it'll fully solve an *easier* problem in the same pattern, front to back, and then send you back to this one.

The reason is simple. Reading a solution feels like learning and isn't. The person who reads the answer to Longest Substring Without Repeating Characters cannot solve Minimum Window Substring next week. The person who derived it can.

Once you've got an accepted submission, the constraint lifts entirely — then it reviews your code, shows the canonical optimal, and compares them. That post-mortem is worth something precisely because you earned it.

## Start with the basics, not with problems

Before any problem, there are **8 foundation topics** — ~16 hours, with 61 free article and video links, built from Striver's A2Z basics:

| Topic | Gates |
|---|---|
| Complexity analysis | **everything** |
| Recursion & the call stack | trees, backtracking, graphs, both DP patterns |
| Sorting | two-pointers, binary search, intervals, greedy |
| Hashing, collections, basic maths, language basics, loop thinking | the rest |

This exists because skipping it is the most common reason people stall. If you can't reason about what a loop costs, the ladder gate below is unpassable — and you won't know whether your solution is good or merely accepted. Claude checks the gate before serving a pattern's first problem, says so once, and lets you push ahead if you want. The override is recorded so your progress report stays honest.

## How it works

Every problem runs through seven gated stages:

| | Stage | You can't leave until |
|---|---|---|
| S0 | Select | — |
| S1 | Pattern | you name the pattern **and** the signal in the constraints that selects it |
| S2 | Intuition | you trace a small input correctly — Claude gives the input, you give the state |
| S3 | Ladder | you give brute / better / optimal with complexities, and what optimal buys |
| S4 | Pseudocode | your algorithm survives an adversarial input |
| S5 | Submit | you get it accepted on leetcode.com |
| S6 | Record | it's reviewed, compared, and written to disk |

**No stage advances on "got it".** Only a produced artifact passes a gate — a trace, a complexity figure, a breaking input.

The gate that does the most work is S2. Claude hands you an input of six characters and asks for the state after each step. You cannot fake that by nodding, and it is the single cheapest way to find out whether an explanation landed.

## What accumulates

```
questions/03-sliding-window/longest-substring-without-repeating-characters.md
```

One file per problem, organized by **pattern** rather than topic — so browsing the tree is itself revision. Each file holds the problem, the signal *in your words*, the invariant *in your words*, your ladder, your pseudocode, the defects found in it, your accepted code, the canonical optimal, and a note to your future self.

After a few months that folder is your own pattern library, written by you, in your language. That's the actual output of this project. The solved count is a side effect.

## Quick start

```bash
git clone <this repo> && cd lets-dsa
```

Open the folder in Claude Code and paste the contents of [`INIT_PROMPT.md`](INIT_PROMPT.md).

That's it. Setup asks about your level, your targets and how much time you actually have, builds a curriculum of 345 problems verified against LeetCode, and orders it so you never hit a difficulty jump you weren't ready for.

## Then

| Type | Gets you |
|---|---|
| `today` | today's problems, sized to your real budget |
| `next` | the next problem in your track |
| `hint` | one rung up the ladder. Costs a rung — they don't reset |
| `park` | save exactly where you are |
| `downgrade` | an easier problem in the same pattern, fully worked |
| `solved` | review, canonical optimal, complexity comparison |
| `visualize <thing>` | an animated explanation, saved to `visuals/` |
| `interview` | mock interview, in persona, with an honest scorecard |
| `progress` | mastery per pattern and a readiness verdict |

## Where the content comes from

Seven curated sheets, merged by LeetCode slug into **345 unique problems**:

| Source | Problems | On LeetCode |
|---|---|---|
| [NeetCode 150](https://neetcode.io/) | 150 | 150 |
| [Striver's A2Z](https://takeuforward.org/dsa/strivers-a2z-sheet-learn-dsa-a-to-z) | 474 | 243 |
| [Striver's SDE Sheet](https://takeuforward.org/dsa/strivers-sde-sheet-top-coding-interview-problems) | 191 | 118 |
| [Blind 75](https://takeuforward.org/dsa/blind-75-leetcode-problems-detailed-video-solutions) | 75 | 66 |
| [Striver's 79](https://takeuforward.org/dsa/strivers-79-last-moment-dsa-sheet-ace-interviews) | 79 | 55 |
| [CodingShuttle CS SDE](https://www.codingshuttle.com/sheets/cs-sde-sheet/) | 169 | 169 |
| [LeetCode "Striver SDE Sheet" list](https://leetcode.com/problem-list/eeudwo2i/) | 117 | 117 |

Plus **the 20 coding patterns** — the taxonomy in `config/patterns.json`, with the recognition signals, invariant shape and common traps for each — and **LeetCode itself** via a pinned [MCP server](https://github.com/jinzcdev/leetcode-mcp-server) for live problem data.

**Company tags are partial and clearly labelled as such.** 42 of the 159 core problems carry companies found by web research, each with the source URL it came from. The rest are empty — and `merged.json` records that empty means *not searched*, not *nobody asks it*. None of it is LeetCode Premium data, which is gated and unavailable.

**Sitting in several sheets is the signal.** No honest public source gives per-problem company tags, but a problem that appears in Blind 75 *and* Striver's 79 *and* NeetCode 150 is one three independent curators thought was worth your time. That's what drives ordering, not invented company labels.

**308 problems live on GeeksforGeeks or Coding Ninjas rather than LeetCode.** They can't run through the loop, which ends in a LeetCode submission — so they're kept in a separate `non_leetcode` block with their step ordering and free article/video links, rather than discarded.

**Two sources couldn't be fetched.** GeeksforGeeks' SDE sheet and Naukri's Code360 list both render client-side — the served HTML has no problem data. Both are recorded in `merged.json` with the reason. GfG's sheet is substantially the same list as Striver's SDE, which is already merged.

Nothing here is invented. If a slug doesn't resolve it's dropped and reported. Every pattern assignment carries a `pattern_source` field saying *how* it was assigned — from a NeetCode category, a hand-split override, or real LeetCode topic tags — so a wrong-looking placement can be audited rather than trusted.

## Free explanations, deliberately not relayed

Most problems carry a free Striver article and YouTube walkthrough in their `resources` block. Claude gives you those **links** when you exhaust the hint ladder — and never reads them and relays the contents during teaching. Relaying an editorial is handing over the solution with a citation attached.

## Honest limitations

- **Claude cannot verify you got Accepted.** Auth is off by default, so "solved" is what you say it is. Turn on `LEETCODE_SESSION` (see `.env.example`) and it becomes a real check.
- **The no-code rule is enforced by prompt, not by machine.** What *is* enforced mechanically: the four MCP tools that could fetch or submit a solution are denied at the project level in `.claude/settings.json`, so Claude cannot look the answer up even if it wanted to.
- **Some problems are LeetCode Premium.** `paid_only` is recorded per problem and setup offers free substitutes.

## Design notes

Every file is markdown or JSON. Every change is git-committed. Nothing lives in a black box — including your progress, which is plain text you can read without this tool.

The project defaults to Sonnet (`.claude/settings.json`), because this is text-heavy teaching rather than hard reasoning, and it costs a fraction of Opus to run.

See [`CLAUDE.md`](CLAUDE.md) for the full operating manual and [`docs/SKILLS.md`](docs/SKILLS.md) for what each skill does.
