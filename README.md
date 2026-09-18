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

That's it. Setup asks about your level, your targets and how much time you actually have, builds a curriculum of 150 problems verified against LeetCode, and orders it so you never hit a difficulty jump you weren't ready for.

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

- **[NeetCode 150](https://neetcode.io/)** — 150 problems across 18 categories. Fetched, and every slug verified against LeetCode's public GraphQL for its real id, difficulty and topic tags.
- **[Striver's A2Z](https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/)** — 18 steps, 474 problems. Used for sequencing.
- **The 20 coding patterns** — the taxonomy in `config/patterns.json`, with the recognition signals for each.
- **LeetCode** — via a pinned [MCP server](https://github.com/jinzcdev/leetcode-mcp-server), for live problem data.

Nothing here is invented. If a slug doesn't resolve, it's dropped and reported rather than guessed at. Company tags are empty rather than fabricated, because LeetCode gates them behind Premium and no honest public source exists.

## Honest limitations

- **Claude cannot verify you got Accepted.** Auth is off by default, so "solved" is what you say it is. Turn on `LEETCODE_SESSION` (see `.env.example`) and it becomes a real check.
- **The no-code rule is enforced by prompt, not by machine.** What *is* enforced mechanically: the four MCP tools that could fetch or submit a solution are denied at the project level in `.claude/settings.json`, so Claude cannot look the answer up even if it wanted to.
- **7 of the 150 problems are LeetCode Premium.** Setup offers free substitutes.

## Design notes

Every file is markdown or JSON. Every change is git-committed. Nothing lives in a black box — including your progress, which is plain text you can read without this tool.

The project defaults to Sonnet (`.claude/settings.json`), because this is text-heavy teaching rather than hard reasoning, and it costs a fraction of Opus to run.

See [`CLAUDE.md`](CLAUDE.md) for the full operating manual and [`docs/SKILLS.md`](docs/SKILLS.md) for what each skill does.
