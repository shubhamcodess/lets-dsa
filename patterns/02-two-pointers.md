# Two Pointers

_Pattern id: 02-two-pointers · Depends on: 01-arrays-hashing · Problems available: 19_

## The one-sentence idea
On sorted or symmetric data, two indices moving toward each other (or one chasing the other) examine every useful pair without examining all pairs.

## How to recognize it
- The input is already sorted, or the problem statement says sorting it "loses nothing" (the answer doesn't depend on original order).
- The task asks for a pair or triplet of elements meeting some sum, difference, or product condition.
- The structure is a palindrome, mirror, or "meet in the middle" shape — something read the same from both ends.
- The task asks to partition the array in place, remove elements in place, or de-duplicate in place without extra space.
- You can describe a brute force as checking every pair with a nested loop, and the sorted order would let you rule out whole ranges of pairs at once.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **Cyclic Sort** | The values are a permutation of 1..n or 0..n-1 and the problem asks for a missing, duplicate, or misplaced number — and wants O(1) extra space | Each value has exactly one correct home index. Repeatedly swap the current element to its home until the position is settled, then a single scan reveals whichever index disagrees with its value |
| **Dutch National Flag / 3-Way Partition** | Sort or group into exactly THREE categories in one pass, in place — 'sort colors', 'partition around a pivot value' | Three pointers: a low boundary, a high boundary, and a scanner. Swap the scanned element to whichever boundary it belongs to and move only the pointers that are safe to move |
| **Two-Pointer** | Problem involves pairs, sorted arrays, triplets, or opposite-end traversal | Use two indices that move towards or away from each other to reduce redundant comparisons |
| **Two-Pointer (Palindrome)** | Problem talks about palindrome checks, symmetric comparison, or reversing from both ends | Compare characters from both ends and move inward until the condition fails |

## The invariant
Everything outside the current [left, right] window has already been decided (included, excluded, or ruled out) and will never need revisiting.

## The shape
1. If the problem allows reordering and isn't already sorted, sort the input first.
2. Place one pointer at each end (or one pointer behind another, depending on the task).
3. Evaluate the condition on the values at the current pointers.
4. Based on whether the condition is too small, too large, or satisfied, move exactly one pointer (or both, if the case demands it) in the direction that fixes the imbalance.
5. Record an answer when the condition is met, and continue narrowing until the pointers cross or meet.
6. When looking for triplets or more, fix one element and run the two-pointer sweep on the remainder, skipping over duplicate fixed elements to avoid repeated answers.

## The named algorithms
Most of this pattern is a recurring pointer-movement idea rather than one canonical algorithm. But a few named algorithms live here too: one for partitioning an array into three groups in a single pass, and a family for locating one string inside another.

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Dutch National Flag (3-way partition) | Rearranges an array of three distinct values so all of one value come first, all of a second value come next, and all of a third come last | Uses three pointers — one marking the boundary of the low group, one scanning forward, one marking the boundary of the high group — and swaps the scanned element into the correct region based on which of the three values it is, shrinking the unknown middle region by one each step | O(n) time, O(1) space |
| Knuth–Morris–Pratt Algorithm | Whether (and where) one string occurs inside another | Precomputes how far the pattern can safely skip ahead on a mismatch, using the pattern's own repeated-prefix structure, so no character of the text is re-examined | O(n + m) time, O(m) space |
| Z Algorithm | For every position in a string, the length of the longest match with the string's own prefix | Maintains a window of the farthest prefix-match found so far and reuses values already computed inside that window rather than recomparing from scratch | O(n) time, O(n) space |
| Boyer–Moore String-Search Algorithm | Whether (and where) one string occurs inside another | Compares the pattern against the text right-to-left and, on a mismatch, uses precomputed tables (based on the mismatched character and the matched suffix) to skip ahead by more than one position, often skipping large stretches of the text entirely | O(n + m) average time (O(n·m) worst case), O(m) space |

## Worked micro-example
Input: sorted array `[1, 2, 4, 6, 8]`, target sum = 10. Task: find a pair that sums to the target.
Start: left = 0 (value 1), right = 4 (value 8).
- Sum = 1 + 8 = 9, which is less than 10. Since the array is sorted, only increasing the left value can raise the sum, so move left forward. Left = 1 (value 2).
- Sum = 2 + 8 = 10. Match found.
Answer: (2, 8). Notice only 2 pairs were checked out of the 10 possible pairs, because each comparison eliminated an entire side of the remaining range.

## Complexity
Typical time is O(n) for a single converging sweep, or O(n log n) if sorting is required first (sorting then dominates). Typical space is O(1) beyond the input, driven by needing only two index variables, unless the output itself requires extra storage (e.g., collecting all triplets).

## Where it breaks
- The data is not sorted and sorting would destroy information the answer needs (such as original index or order of appearance).
- The condition isn't monotonic in the sorted order — moving a pointer doesn't predictably move the result in one direction, so you can't tell which pointer to advance.
- The relationship between elements isn't pairwise but depends on a non-contiguous subset or a running aggregate that isn't just "sum of two values."

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Sliding Window | Sliding Window tracks a *contiguous* range and a condition that changes as elements enter/exit; Two Pointers often looks at just the two boundary elements, not everything between them. |
| Binary Search | Both exploit sorted order, but binary search discards half the space per step on a single search value, while two pointers move gradually and track two positions at once. |
| Arrays & Hashing | If the pair-sum problem is unsorted and you don't want to sort (to preserve indices), a hash table lookup replaces the second pointer. |

## Common traps
- Moving both pointers when only one should move, which can skip over the correct pair.
- Forgetting to skip duplicate values when advancing past a fixed element in 3Sum/4Sum-style problems, causing the same triplet to be emitted twice.
- Off-by-one errors at the boundary when the pointers meet or cross, especially in palindrome checks.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Merge Sorted Array | Easy | 3 |
| Remove Duplicates from Sorted Array | Easy | 3 |
| 3Sum | Medium | 7 |
| Next Permutation | Medium | 5 |
| Sort Colors | Medium | 4 |
| 4Sum | Medium | 3 |
| Container With Most Water | Medium | 3 |
| Trapping Rain Water | Hard | 6 |
