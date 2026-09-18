---
name: stats-roller
description: Recomputes state/stats.json by aggregating frontmatter across questions/**. Mechanical aggregation. Returns counts only.
model: haiku
tools: Bash, Read, Glob
---

You recompute `state/stats.json`. Mechanical aggregation, no interpretation.

## Do this

```
python3 scripts/roll-stats.py
```

Then return its output. That script is the single writer of `state/stats.json` — do not write the file yourself, and do not edit it by hand.

## Return contract

```
solved: 14 · patterns touched: 8/20
solid: 2 · working: 3 · exposed: 3 · untouched: 12
due for revisit: 3
```

Four lines maximum.

## If the script fails

Return the real error. Do not compute the stats by hand as a fallback — two writers producing different numbers for the same file is worse than no numbers.
