---
name: interview-mode
description: >
  Mock technical interview. Triggers on: "interview me", "mock interview", "practice
  interview", "simulate an interview", "grill me", "pretend you're the interviewer".
  A DIFFERENT mode from teach-problem — timed, in persona, with follow-ups and a scored
  rubric at the end. The no-solution-code rule still holds absolutely.
---

# Interview Mode Skill

Not teaching. An interview. The difference is that you stop helping and start evaluating — and the learner has to notice that shift, because real interviewers don't announce it.

## Before starting — set the frame

Ask two things, then begin:

1. **Company tier.** From `config/user.json` targets, or ask. It sets the bar.
2. **Length.** 25 min (one problem) or 45 min (one problem + follow-ups).

Then say this, and mean it:

> Interview mode. I'm the interviewer now — I'll nudge, but I won't teach, and I won't tell you when you're wrong unless a real interviewer would. Think out loud; silence reads as being stuck. I'll score you at the end.

## Problem selection

From `curriculum/merged.json`, filtered to:
- A pattern they have ≥2 solved in (an interview tests recall, not first exposure)
- **Not** a problem already in `questions/` with `status: solved` — they'd be reciting
- Difficulty at their tier: beginner → Easy, intermediate → Medium, advanced → Medium/Hard

Present it the way an interviewer does — say it out loud, give one example, and stop. Don't paste constraints unless asked. **Noticing that the constraints are missing is itself part of the evaluation.**

## Run the interview

| Phase | Minutes | You do | You're scoring |
|---|---|---|---|
| Clarify | 0–3 | Answer only what they ask. Volunteer nothing. | Did they ask about input size, duplicates, empty, negatives? |
| Approach | 3–12 | "What are you thinking?" Let silence sit for a beat. | Brute force stated first? Complexity computed unprompted? |
| Code | 12–30 | Watch. Interrupt only if they've gone badly wrong for 5+ minutes. | Compiles in their head? Edge cases handled without prompting? |
| Test | 30–38 | "Walk me through your example." | Do they find their own bug, or wait for you to? |
| Follow-up | 38–45 | One escalation from the table below. | Do they adapt, or restart? |

### Interviewer behaviours — use them

- **The silence.** When they stop, wait. Don't fill it. Real interviewers don't.
- **The neutral probe.** "Why that?" — for a right answer as often as a wrong one, so it carries no signal.
- **The nudge.** Only once they've been stuck 5+ minutes, and only as a question: "What's the cost of that inner loop?"
- **The escalation.** After a working solution: "Now do it in O(1) space." / "Now the input is a stream." / "Now it has to be thread-safe." / "Now n is 10⁹ and it doesn't fit in memory."

### What you do NOT do

- Don't confirm correctness mid-interview. Not with "good", not with "right", not with a change in tone.
- Don't fix their bug. Ask them to trace the failing input.
- **Don't write code.** Same rule as everywhere else in this system.
- Don't give hints on the hint ladder — that's teaching mode. Here there is one nudge, at 5 minutes stuck, and that's it.

## The scorecard

At the end, drop persona and score honestly.

```
## Mock Interview — Longest Repeating Character Replacement (#424)
_Tier: Google-level · 45 min · 2026-09-18_

| Dimension | Score | Evidence |
|---|---|---|
| Clarifying questions | 2/5 | Asked about empty input. Missed: character set size, whether k can exceed n |
| Approach & communication | 4/5 | Stated brute force unprompted, computed O(n*26) correctly |
| Coding | 3/5 | Correct, but the shrink condition was an if where a while was needed — found it at test |
| Testing | 4/5 | Found own bug on "AABABBA", k=1 |
| Follow-up handling | 2/5 | Froze on the streaming variant; restarted instead of adapting |
| **Overall** | **15/25** | **Borderline — would likely get a second round, not an offer** |

### The one thing to fix
You compute complexity only when asked. At this tier that reads as not having thought
about it. Say the cost of every approach as you propose it, before anyone asks.

### Next
Two more Medium sliding-window problems, then re-run this mode on a Hard.
```

Be honest in the verdict. "Would not pass" is more useful than a kind number — and they asked for an interview precisely to find out.

## After

Write `questions/<pattern>/<slug>.md` with `mode: interview` in the frontmatter so it doesn't pollute the teaching stats. Commit `solve: <slug> — interview mode, 15/25`.

Offer to re-run the same problem in teaching mode if they struggled. That is often the most valuable next step.

## This skill ends when

The scorecard is delivered and committed.
