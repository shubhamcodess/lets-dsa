# Linked List

_Pattern id: 07-linked-list · Depends on: 02-two-pointers · Problems available: 22_

## The one-sentence idea
Pointer surgery: since you cannot index into the middle of a linked list, you keep exactly the references you need and rewire connections carefully, one link at a time.

## How to recognize it
- The input is explicitly a linked list, not an array — described node by node with a "next" (and sometimes "random" or "prev") reference.
- The task asks to reverse, merge, reorder, or remove elements in place, working with the existing nodes rather than building a new structure from scratch.
- The problem explicitly demands O(1) extra space on a list, ruling out the shortcut of copying values into an array to solve it there.
- The description mentions traversing "from the front only" — no indexing, no jumping backward without a stored reference.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **Basic DLL Operations** | Problem mentions insertion/deletion in DLL, printing forwards/backwards, or caching (LRU/MRU/frequency-based) | Maintain prev and next pointers carefully for insert, delete, traversal; use DLL + HashMap for O(1) cache operations |
| **Reversal Pattern** | Problem mentions reversing nodes or rearranging linked list order | Reverse entire list, partial list, or groups to reorder nodes |

## The invariant
At every step, the already-processed prefix of the list is fully and correctly rewired, and the not-yet-processed suffix is still intact and reachable from wherever the current pointer sits.

## The shape
1. Set up a "dummy" placeholder node before the real head when the head itself might change or be removed, so every node — including the first — is treated uniformly.
2. Keep one or more pointers marking your current position(s) in the list: often a "current" pointer, sometimes a "previous" pointer trailing behind it, sometimes a second pointer moving at a different speed or a fixed distance ahead.
3. At each step, before changing any `next` reference, save a reference to whatever node you'd otherwise lose access to (typically the node currently pointed to by `next`).
4. Rewire the `next` pointer(s) of the current node(s) to reflect the new structure (reversed direction, merged order, or skipped node).
5. Advance your pointer(s) forward using the saved reference from step 3, so you never follow a `next` pointer that you've already overwritten.
6. Continue until the traversal condition is met (reaching the end, reaching a specific count, or two pointers meeting), then reconnect to the dummy node's successor to get the real head, if a dummy was used.

## The named algorithms
Most pointer-rewiring maneuvers here (reversal, merging) are techniques reapplied per problem rather than named algorithms. But two genuinely named algorithms live in this pattern: one for detecting a cycle without extra memory, and one for sorting a list without random access.

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Floyd's Cycle Finding Algorithm | Whether a linked list contains a cycle, and (in its extended form) where that cycle begins | Runs two pointers through the list at different speeds — one advancing one node at a time, the other two nodes at a time. If a cycle exists, the faster pointer eventually laps the slower one inside the loop; if it doesn't, the faster pointer reaches the end first. A second phase (resetting one pointer to the head and advancing both at equal speed) locates the cycle's starting node. | O(n) time, O(1) space |
| Merge Sort (on a linked list) | A fully sorted version of the list | Repeatedly splits the list in half (found via a fast/slow pointer instead of indexing), recursively sorts each half, and merges the two sorted halves back together by relinking nodes rather than copying values — the same divide-and-conquer structure as array merge sort, adapted to a structure with no random access | O(n log n) time, O(log n) space for the recursion (O(1) extra beyond that, since nodes are relinked in place rather than copied) |

## Worked micro-example
Input: linked list `1 -> 2 -> 3 -> None`. Task: reverse it in place.
Start: `previous = None`, `current = node(1)`.
- At node 1: save `next_node = node(2)` (otherwise it would be lost). Point node 1's `next` to `previous` (None), so node 1 now points to None. Advance: `previous = node(1)`, `current = node(2)`.
- At node 2: save `next_node = node(3)`. Point node 2's `next` to `previous` (node 1), so node 2 now points to node 1. Advance: `previous = node(2)`, `current = node(3)`.
- At node 3: save `next_node = None`. Point node 3's `next` to `previous` (node 2), so node 3 now points to node 2. Advance: `previous = node(3)`, `current = None`.
Traversal ends because `current` is None. The new head is `previous`, which is node 3.
Result: `3 -> 2 -> 1 -> None`. Each node's `next` was rewritten exactly once, and the "save before overwrite" step is what kept the rest of the list reachable throughout.

## Complexity
Typical time is O(n), driven by a single pass (or two passes, for problems needing a length or a second traversal) over the list's nodes. Typical space is O(1) for iterative pointer manipulation, driven by needing only a constant number of pointer variables; a recursive formulation would instead cost O(n) call-stack space.

## Where it breaks
- The problem needs random access by position (e.g., "get the k-th smallest" without traversal) — a linked list only supports sequential access, so this pattern doesn't help there.
- The manipulation genuinely needs to know values across the whole structure at once in a way that can't be discovered by a single forward pass (unless a two-pass or fast/slow technique specifically resolves it, like finding a cycle or the middle).
- The structure isn't actually list-shaped (it's a tree or graph with branching), so "next pointer" rewiring doesn't generalize.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Two Pointers | Fast/slow pointer techniques on a linked list are a direct application of Two Pointers, but here the "positions" are node references, not array indices, and pointers move via `next`, not arithmetic. |
| Stack | Reversing or processing a linked list recursively implicitly uses a call stack; an explicit stack can substitute for recursion, but the recognition signal is still "this is a list," not "this needs LIFO order." |
| Arrays & Hashing | Problems like detecting a cycle or intersection could be solved with a hash set of visited node references, but that costs O(n) space — the linked-list-native solution instead exploits pointer movement for O(1) space. |

## Common traps
- Losing the rest of the list by reassigning a node's `next` pointer before saving a reference to what it used to point to.
- Not using a dummy head node, which forces special-casing whenever the real head itself might be removed or replaced.
- Mishandling the fast/slow pointer starting positions or step sizes, producing an off-by-one error when locating the middle node or detecting a cycle.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Reverse Linked List | Easy | 6 |
| Merge Two Sorted Lists | Easy | 5 |
| Middle of the Linked List | Easy | 5 |
| Intersection of Two Linked Lists | Easy | 4 |
| Remove Nth Node From End of List | Medium | 7 |
| Add Two Numbers | Medium | 5 |
| Copy List with Random Pointer | Medium | 4 |
| Reverse Nodes in k-Group | Hard | 5 |
