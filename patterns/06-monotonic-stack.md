# Monotonic Stack

_Pattern id: 06-monotonic-stack · Depends on: 05-stack · Problems available: 7_

## The one-sentence idea
A stack kept sorted (increasing or decreasing) discards elements that can never be the answer for anything later, giving next-greater / previous-smaller style answers in linear time.

## How to recognize it
- The problem asks for the next greater element, next smaller element, or the "span" of how far a value's influence reaches (looking left or right until something bigger/smaller appears).
- The shape is a histogram, skyline, or "trapping rain water" style problem — bars or heights where you need to know what's bigger nearby.
- You can describe the brute force as: for each element, scan forward (or backward) until you find the first element that's bigger (or smaller) than it — a nested loop where the inner loop is a directional search for a threshold crossing.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **Monotonic Stack** | Problem mentions “next greater/smaller element,” spans, or trapping area | Maintain a monotonic increasing/decreasing stack to find next/prev greater/smaller, histogram ranges, or collisions |

## The invariant
The stack is always kept monotonic (strictly increasing or strictly decreasing from bottom to top); anything popped off was made irrelevant by the very element that popped it.

## The shape
1. Walk through the input from left to right (or right to left, depending on the question), keeping a stack of candidate elements.
2. Before pushing the current element, compare it against whatever is on top of the stack.
3. While the top of the stack violates the required order relative to the current element (e.g., the top is smaller than the current element, when looking for "next greater"), pop it — the current element has just resolved that popped element's answer (it is that element's next greater/smaller neighbor).
4. After popping everything that the current element resolves, push the current element onto the stack.
5. Continue until the input is exhausted; anything left on the stack at the end has no qualifying neighbor within the input.
6. When the question needs distance or width (like a histogram area), store indices on the stack instead of values, so the gap between positions can be computed when a pop happens.

## The named algorithms
This pattern is a technique, not a named algorithm family. There is no separately-named algorithm beyond "monotonic stack" itself — every problem here is the same discard-what-can't-matter idea applied to a different notion of "greater," "smaller," or "area."

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|

## Worked micro-example
Input: array `[2, 1, 5, 3]`. Task: for each element, find the next greater element to its right (or none).
Walk right to left, keeping a stack that stays decreasing from bottom to top.
- Index 3, value 3: stack is empty, so no next greater exists for it. Push 3. Stack: [3].
- Index 2, value 5: top of stack is 3, which is not greater than 5, so pop it. Stack is now empty, so no next greater exists for 5 either. Push 5. Stack: [5].
- Index 1, value 1: top of stack is 5, which is greater than 1. So 5 is the next greater element for 1. Push 1. Stack: [5, 1].
- Index 0, value 2: top of stack is 1, not greater than 2, so pop it. New top is 5, which is greater than 2. So 5 is the next greater element for 2. Push 2. Stack: [5, 2].
Answer: next-greater(2)=5, next-greater(1)=5, next-greater(5)=none, next-greater(3)=none. Each element was pushed once and popped at most once, rather than each element scanning forward through the rest of the array.

## Complexity
Typical time is O(n), driven by the fact that each element is pushed onto the stack exactly once and popped at most once across the entire walk, even though it looks like nested loops. Typical space is O(n) in the worst case, driven by an already-monotonic input needing the entire array held on the stack at once.

## Where it breaks
- The comparison needed isn't about "next bigger/smaller in one direction" — for example, if you need the maximum over an arbitrary sliding range rather than a directional next-crossing, a different structure (like a monotonic deque, which still uses the same discard idea but from both ends) may be needed instead.
- The relevant relationship between elements isn't ordered at all (no notion of "greater" or "smaller" applies to the comparison the problem wants).
- Elements popped might actually still be needed later for a different, unrelated query — the "safe to discard forever" property is what makes the whole approach valid, and if it doesn't hold, the stack invariant breaks.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Stack | A plain stack matches openers with closers by nesting order; a monotonic stack actively evicts elements based on a value comparison, not a matching relationship. |
| Sliding Window | Sliding Window Maximum can be solved with a monotonic deque, but the recognition signal for that problem is "contiguous range," while pure monotonic-stack problems (next greater, histogram) have no window at all. |
| Binary Search | Both can compute "how far until a threshold is crossed," but binary search needs sorted, static data with random access, while monotonic stack processes a sequence in one pass with no sorting required. |

## Common traps
- Storing values on the stack when the answer actually needs the distance between positions (width, span), which requires storing indices instead.
- Getting the strictness wrong (using `>` when `>=` was needed, or vice versa), so equal elements are either double-counted or never resolved.
- Popping in the wrong direction relative to the walk (confusing "next greater" with "previous greater"), which silently answers a different question than the one asked.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Next Greater Element I | Easy | 4 |
| Online Stock Span | Medium | 3 |
| Daily Temperatures | Medium | 2 |
| Car Fleet | Medium | 1 |
| Next Greater Element II | Medium | 1 |
| Sum of Subarray Ranges | Medium | 1 |
| Largest Rectangle in Histogram | Hard | 6 |
