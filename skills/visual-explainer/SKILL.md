---
name: visual-explainer
description: >
  Builds animated visual explanations of a data structure, algorithm, or the mechanism
  behind a specific problem. Triggers on: "show me", "visualize", "animate", "draw this",
  "I can't picture it", "what does that look like", "show me how the pointers move",
  "explain visually". Produces an inline sketch immediately plus a saved self-contained
  HTML animation under visuals/<pattern>/. Obeys the no-solution-code rule — it animates
  the MECHANISM, never a solution the learner has not yet derived.
---

# Visual Explainer Skill

Some things do not land as prose. A window that grows and shrinks, a recursion tree unwinding, a heap sifting up — these are motion, and describing motion in sentences is the long way round.

## The guardrail applies here too

**Before the learner has an accepted submission, you may animate the pattern's mechanism but NOT this problem's solution.**

| Stage | Allowed |
|---|---|
| S1–S2 | The pattern in the abstract, on a **different** input than the problem's. "How a window slides" on `"aabbcc"` — never the problem's own example. |
| S3–S4 | Data structure behaviour only. A heap sifting, a trie inserting, a stack popping. |
| S5 | Nothing. They're submitting. |
| S6+ | Anything. Animate their solution, animate the canonical, animate both side by side. |

Animating this problem's optimal algorithm at S2 hands over the answer in a prettier wrapper. It is the same violation.

---

## Two outputs, every time

### 1. Inline sketch — immediately

Use `mcp__visualize__show_widget`. Call `read_me` first (silently — don't narrate it).

Keep it small: one concept, 3–6 frames, no controls beyond what's needed. This is the "oh, I see" moment, and it should arrive in the same message they asked.

### 2. Saved HTML — for keeps

Delegate to the `visual-builder` agent. It writes the file and returns a path; it must not return the HTML itself.

Path: `visuals/<NN>-<pattern>/<concept-slug>.html`
Example: `visuals/03-sliding-window/window-grow-shrink.html`

Then tell them where it is and offer to open it in the browser pane.

---

## What the saved HTML must contain

A single self-contained file. No CDN, no build step, no network at runtime.

**Required:**
- Play / Pause / Step-forward / Step-back / Reset controls
- A step counter: `Step 4 of 11`
- A narration line under the canvas that changes per step, saying **why** this step happens — not what moved, but why it had to
- The invariant displayed persistently, highlighted red the moment it breaks and green when restored. **This is the single most useful element; do not omit it.**
- Speed control (0.5× / 1× / 2×)
- Works at phone width, no horizontal scroll
- Light and dark mode via `prefers-color-scheme`, with an explicit background on `body`

**Forbidden:**
- Any external script or stylesheet
- Solution code displayed on screen, unless the learner has reached S6 on this problem
- Auto-play on load — it starts paused at step 0, so they can read the setup

**Structure:** the animation is a list of states, rendered by a pure function of `stepIndex`. Not an imperative sequence of timeouts — that can't step backwards, and stepping backwards is where the understanding happens.

```
const steps = [
  { arr: [...], left: 0, right: 0, window: [], invariantOk: true,
    note: "Both pointers start at index 0. The window is empty, so it trivially has no duplicates." },
  ...
];
```

---

## Choosing what to animate

| They're stuck on | Animate |
|---|---|
| "why does the pointer move there" | The two pointers, with the invariant banner breaking and being repaired |
| "I don't get recursion" | The call stack growing and unwinding, with each frame's local state visible |
| "what does the dp table mean" | The table filling cell by cell, with arrows to the cells each one reads |
| "how does a heap work" | Sift-up and sift-down as tree + array simultaneously, so the index arithmetic stops being magic |
| "why is this O(n) not O(n²)" | A counter of total operations ticking up next to n — the amortized argument made visible |
| **anything else** | Ask what specifically they can't picture. "Visualize this problem" is too broad to be useful. |

## Reuse before you build

Check `visuals/<pattern>/` first. If a fitting animation exists, open that instead of generating a near-duplicate. Building a second sliding-window animation because the filename didn't match is waste.

## After building

Commit `visual: <concept-slug> for <pattern>`.
Link it from the question file's `## Intuition` section if it was built for a specific problem.

## This skill ends when

The inline sketch is shown and the file is written and committed. Return to whatever stage the loop was in — say the stage banner again so they know where they are.
