# Fast & Slow Pointers

_Pattern id: 08-fast-slow-pointers · Depends on: 07-linked-list · Problems available: 2_

## The one-sentence idea
Two pointers walk the same sequence at different speeds, and the gap between them (or the fact that they collide at all) tells you something about the sequence's shape that a single pass could not.

## How to recognize it
- The problem is about a linked list, or a sequence that behaves like one (each element points to, or maps to, the "next" one).
- It asks whether the structure loops back on itself — a cycle, a repeat, an infinite chain.
- It asks for the middle element, or the nth element from the end, in one pass without knowing the length up front.
- A number range is dressed up as an implicit linked list: values in `[1, n]` used as indices into an array of length `n+1`, where following "value at index" repeatedly is really walking a chain.
- "Without extra space" or "in O(1) memory" is emphasized, ruling out the obvious hash-set solution.

## The invariant
Fast has always travelled exactly twice slow's distance, so if a cycle exists, fast eventually laps slow and they occupy the same node.

## The shape
1. Start two pointers at the same place — usually the head of the structure.
2. Advance the slow pointer one step at a time; advance the fast pointer two steps at a time, each iteration.
3. Stop when fast reaches the end (no cycle) or when fast and slow point to the same element (cycle found).
4. If only detection was asked, the answer is now known.
5. If the cycle's entry point is needed: reset one pointer to the start, leave the other at the meeting point, then advance both one step at a time — they meet again exactly at the entry point.
6. If the middle was asked: when fast reaches the end, slow is at the middle (adjust the stopping condition by one step for even-length inputs depending on which middle is wanted).
7. If the nth-from-the-end was asked: advance a lead pointer n steps first, then move both pointers together until the lead reaches the end — the trailing pointer is now n from the end.

## The named algorithms

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Floyd's cycle detection (tortoise and hare) | Whether a sequence of pointers/mappings contains a cycle, and where it begins | A pointer moving twice as fast as another must eventually re-enter the cycle and lap the slow pointer; the distance from the meeting point back to the entry equals the distance from the start to the entry | O(n) time, O(1) space |

Floyd's algorithm is the entire pattern. The proof that a second walk from the head, moving one step at a time alongside the meeting point, lands exactly on the cycle's entry is a short piece of modular arithmetic on the cycle length — worth working through once so the "reset one pointer" step in the shape above feels earned rather than memorized.

## Worked micro-example
Sequence: nodes A → B → C → D → B (D points back to B, forming a cycle B-C-D-B).

- Start: slow = A, fast = A.
- Step 1: slow → B, fast → C (two hops: A→B→C).
- Step 2: slow → C, fast → B (fast: C→D→B).
- Step 3: slow → D, fast → D (fast: B→C→D). Slow and fast are both at D — cycle detected.
- To find the entry: reset pointer1 = A, keep pointer2 = D. Move both one step at a time.
  - pointer1: A → B. pointer2: D → B.
  - Both land on B simultaneously. B is the cycle's entry point.

## Complexity
Time is O(n), where n is the number of nodes traversed before a cycle is found or the end is reached — fast never revisits more than one extra lap of the cycle, so the total work is linear, not quadratic. Space is O(1): only two pointers are kept, regardless of input size, which is the entire reason this pattern replaces a hash-set-based visited check.

## Where it breaks
It only helps when "next" is well defined and single-valued — a plain array with arbitrary jumps forward and backward, or a graph with branching, has no single deterministic path to walk, so there is no meaningful "lap." It also does not directly give you extra information about *what* is inside the cycle (values, sum, etc.) — only where it starts, so problems asking for properties of the cyclic portion need a second pass after detection.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Two pointers (opposite ends) | Two pointers converge from both ends of a sorted/bounded array toward each other; fast-slow pointers move in the *same* direction at different speeds through a chain. |
| Hash-set visited tracking | Both detect repeats/cycles, but a hash set costs O(n) space; fast-slow trades that space for the twice-speed trick and is the expected answer when O(1) space is required. |

## Common traps
- Null-dereferencing by checking `fast.next.next` before confirming `fast` and `fast.next` are both non-null — the order of the null checks matters.
- Stopping as soon as a meeting point is found when the question actually wants the cycle's entry node, which needs the second walk from the head.
- Off-by-one errors when using fast-slow to find "the middle": whether fast starts one step ahead, and whether the loop condition is `fast` or `fast.next`, changes which of the two middle nodes you land on for even-length lists.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Linked List Cycle | Easy | 7 |
| Find the Duplicate Number | Medium | 4 |
