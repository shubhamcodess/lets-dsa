# Sliding Window

_Pattern id: 03-sliding-window · Depends on: 02-two-pointers · Problems available: 14_

## The one-sentence idea
A contiguous range that grows on the right and shrinks on the left, so each element is added to the window once and removed once, instead of every range being rescanned from scratch.

## How to recognize it
- The problem asks about a contiguous subarray or substring, not any subset.
- It asks for the longest, shortest, maximum, or minimum such range subject to some condition (a sum limit, a character constraint, at most/exactly K of something).
- The condition has a "breakable and repairable" quality: adding an element can violate it, and removing an element from the front can restore it.
- You can imagine checking every contiguous range with two nested loops (outer = start, inner = end), and notice that as the start moves forward, most of the work from the previous range is still valid.

## The invariant
The window always satisfies the condition (or is the smallest/first violation of it), and the best window seen so far is remembered as the running answer.

## The shape
1. Start with both window boundaries at the beginning of the input, and initialize whatever running state describes the window's content (a sum, a count map, a count of distinct items).
2. Extend the right boundary one step at a time, folding the newly included element into the running state.
3. After each extension, check whether the window still satisfies the required condition.
4. If it doesn't (or, for some problems, if it does and you're looking for the shortest window), shrink from the left one step at a time, removing each excluded element's contribution from the running state, until the condition is restored.
5. At each valid configuration, compare the current window against the best answer recorded so far and update if it's better.
6. Continue until the right boundary has swept the entire input.

## The named algorithms
This pattern is a technique, not a named algorithm family. The idea of two moving boundaries with incrementally maintained state is reused across every problem in this category rather than being a single textbook algorithm with a name.

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|

## Worked micro-example
Input: array `[2, 1, 5, 1, 3, 2]`, target sum ≤ 8. Task: find the length of the longest contiguous subarray with sum at most 8.
Start: left = 0, right = 0, running sum = 0, best length = 0.
- Add index 0 (value 2): sum = 2. Within limit. Window is [0,0], length 1. Best = 1.
- Add index 1 (value 1): sum = 3. Within limit. Window [0,1], length 2. Best = 2.
- Add index 2 (value 5): sum = 8. Within limit. Window [0,2], length 3. Best = 3.
- Add index 3 (value 1): sum = 9. Exceeds limit. Shrink from left: remove index 0 (value 2), sum = 7. Window [1,3], length 3. Best stays 3.
- Add index 4 (value 3): sum = 10. Exceeds limit. Shrink: remove index 1 (value 1), sum = 9. Still exceeds. Shrink: remove index 2 (value 5), sum = 4. Window [3,4], length 2.
- Add index 5 (value 2): sum = 6. Within limit. Window [3,5], length 3. Best stays 3.
Answer: 3. Every element was added once and removed at most once, rather than every one of the 21 possible subarrays being summed separately.

## Complexity
Typical time is O(n), driven by the fact that each element is added to the window exactly once and removed at most once across the whole sweep. Typical space is O(1) to O(k), driven by whatever running state the window keeps (a single sum needs O(1); a character-frequency map needs space proportional to the alphabet or distinct-element count).

## Where it breaks
- The range of interest doesn't need to be contiguous (any subset qualifies) — sliding window only tracks a contiguous block.
- The condition is not "breakable and repairable" by adding/removing at the ends — for example, if shrinking from the left can both help and hurt the condition unpredictably, there's no clean direction to move.
- The window's required state can't be updated incrementally (recomputing it from scratch on every move would erase the efficiency gain).

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Two Pointers | Two Pointers often only cares about the two boundary values themselves; Sliding Window cares about the aggregate state of everything between the boundaries. |
| Monotonic Stack | Sliding Window Maximum can be solved with a monotonic deque, but the recognition signal is still "contiguous range" — the monotonic structure is an implementation detail, not the identifying feature. |
| Arrays & Hashing | A frequency map inside a sliding window looks like plain hashing, but the map's contents change dynamically as the window moves, which hashing-alone problems don't require. |

## Common traps
- Shrinking with an `if` when a `while` is needed, so the window doesn't fully repair itself after a violation before you check the condition again.
- Recomputing the window's state (sum, distinct count, etc.) from scratch on every move instead of updating it incrementally, which quietly turns an O(n) solution into O(n²).
- Forgetting to update the best answer inside the loop that shrinks the window, missing the exact point where the window becomes valid or optimal.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Best Time to Buy and Sell Stock | Easy | 6 |
| Longest Substring Without Repeating Characters | Medium | 6 |
| Longest Repeating Character Replacement | Medium | 4 |
| Binary Subarrays With Sum | Medium | 1 |
| Count Number of Nice Subarrays | Medium | 1 |
| Find All Anagrams in a String | Medium | 1 |
| Sliding Window Maximum | Hard | 6 |
| Minimum Window Substring | Hard | 4 |
