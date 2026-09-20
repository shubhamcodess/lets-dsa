# Binary Search

_Pattern id: 04-binary-search · Depends on: 01-arrays-hashing · Problems available: 31_

## The one-sentence idea
Halve a search space that has a monotonic yes/no property — the array itself need not be the search space; the space can be a range of possible answers.

## How to recognize it
- The input is sorted, or a rotated/partially-sorted version of a sorted structure.
- The constraints are large enough that checking every candidate one by one (O(n) per query, or an O(n) scan) would be too slow.
- The problem asks for the minimum value that satisfies some property, or the maximum value that still satisfies it ("smallest X such that...", "largest capacity such that...").
- You can imagine writing a yes/no check for a candidate value, and that check is false for small candidates and becomes true for large candidates (or vice versa) without flipping back and forth.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **Binary Search on Answers** | Problem mentions minimum/maximum feasible value or optimization over a range | Treat answer space as sorted → binary search to find minimum/maximum feasible value |
| **Classic Binary Search** | Problem mentions a sorted array or “find element efficiently.” | Divide-and-conquer → narrow search space in sorted array |

## The invariant
The answer is always inside the current [lo, hi] range; every half discarded at each step has been proven not to contain it.

## The shape
1. Identify the search space: it might be array indices, or it might be a range of possible answer values (like "minimum speed" or "maximum distance").
2. Set the lower and upper bounds of that space.
3. Repeatedly compute the midpoint of the current range.
4. Apply a test at the midpoint: for array search, compare against the target; for "search on the answer," run a feasibility check that answers yes or no.
5. Use the test's result to discard the half of the range that cannot contain the answer, keeping the half that can.
6. Stop when the range narrows to a single point, and that point is the answer (or confirm it directly, depending on the problem).

## The named algorithms
Unlike most other patterns in this set, this one is built entirely out of a small number of named ideas — binary search itself, its generalization to answer ranges, and the divide-and-conquer principle it's a special case of.

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Binary Search | The position of a target value in a sorted sequence, or whether it's present at all | Repeatedly compares the target against the middle element and discards the half of the range that provably cannot contain it, maintaining the invariant that the answer always lies within the shrinking [lo, hi] range | O(log n) time, O(1) space |
| Binary Search on the Answer Space | The smallest (or largest) value in a range of candidate answers for which a yes/no feasibility check holds | Instead of searching the input array, treats the space of possible *answers* as the sorted, monotonic structure — a candidate answer is fed into a feasibility check that is false for all values on one side and true for all values on the other, so the same halving logic finds the exact boundary between them | O(log(range) × cost of one feasibility check), O(1) extra space |
| Divide and Conquer | Solves a problem by splitting it into independent subproblems, solving each, and combining the results | Splits the input (often at a midpoint), recursively solves both halves, and merges the two solutions in a way that accounts for interactions crossing the split point — binary search is the degenerate case where only one half needs to be recursed into | Typically O(n log n) or O(log n) depending on how much combining work is needed at each level; O(log n) space from the recursion, unless done iteratively |

## Worked micro-example
Input: sorted array `[1, 3, 5, 7, 9, 11]`, target = 7. Task: find the index of the target.
Start: lo = 0, hi = 5.
- mid = 2, value = 5. 5 < 7, so the target must be to the right. Set lo = 3.
- mid = 4, value = 9. 9 > 7, so the target must be to the left. Set hi = 3.
- mid = 3, value = 7. Match found at index 3.
Answer: index 3. Only 3 elements were examined out of 6, and the range halved each time: 6 candidates, then 3, then 1.

## Complexity
Typical time is O(log n) for array-index search, or O(log(range) × cost-of-check) when searching over an answer range, driven by the number of times the space can be halved before one element remains. Typical space is O(1) for the iterative form, driven by needing only the lo/hi/mid variables (a recursive form would add O(log n) call-stack space).

## Where it breaks
- The data has no monotonic structure at all — no sorted order and no feasibility check that is false-then-true (or true-then-false) across the range.
- The property being tested can be true, then false, then true again as the candidate increases — halving would then discard a half that might contain the answer.
- The input size is small enough that a linear scan is simpler and the log-factor savings don't matter, or the structure changes between queries (making repeated re-sorting more expensive than it's worth).

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Two Pointers | Both exploit sorted order, but two pointers track two positions moving gradually toward each other, while binary search jumps by halving and only tracks one candidate at a time. |
| Sliding Window | Sliding window problems are about contiguous ranges of the input; binary-search-on-answer problems are about a numeric property, not a subrange of the array. |
| Arrays & Hashing | If you just need to know whether a value exists and don't care about "closest" or "boundary," a hash table can answer it in O(1) without needing sorted order at all. |

## Common traps
- An infinite loop caused by the wrong mid rounding (e.g., always rounding down when lo and hi are adjacent, so the range never shrinks).
- Searching directly on the array's values when the actual monotonic property lives in a derived answer range instead ("search on the answer").
- Getting the boundary condition backwards — returning the last "no" instead of the first "yes," or vice versa, at the point where the property flips.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Binary Search | Easy | 3 |
| Find Minimum in Rotated Sorted Array | Medium | 5 |
| Search a 2D Matrix | Medium | 5 |
| Search in Rotated Sorted Array | Medium | 5 |
| Koko Eating Bananas | Medium | 3 |
| Find Peak Element | Medium | 2 |
| Median of Two Sorted Arrays | Hard | 5 |
| Reverse Pairs | Hard | 3 |
