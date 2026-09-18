# Backtracking

_Pattern id: 12-backtracking · Depends on: 09-trees · Problems available: 15_

## The one-sentence idea
Enumerate a decision tree of choices one branch at a time, and undo each choice the moment you back out of it, so the state is exactly clean for the next branch to try.

## How to recognize it
- The problem asks for all combinations, permutations, subsets, or valid arrangements — not just one, or a count, but the actual set of them.
- The input size n is small, and the answer space grows factorially or exponentially (a strong hint that a full brute-force enumeration is actually intended, not a shortcut).
- Constraint satisfaction framed as placing things one at a time under rules — sudoku, n-queens, word search on a grid, partitioning a string so every piece satisfies a property.
- The phrase "generate all ways to..." or "return all possible..." appears in the prompt.
- Choices must be made in sequence, and a choice made early can make later choices invalid (so some branches must be abandoned partway through).

## The invariant
On entering a node of the decision tree, the current state reflects exactly the sequence of choices made on the path from the root to here; on leaving that node, every one of those choices is undone, restoring the state to what it was before the node was entered.

## The shape
1. Define the state that represents "the choices made so far" (a partial combination, a partially filled board, a partial path).
2. Define the base case: when the partial state is actually a complete, valid answer — record a copy of it.
3. At each step, enumerate every choice available from the current state.
4. For each choice: check whether it's still valid given everything chosen so far (pruning); if not, skip it immediately without recursing.
5. If valid, apply the choice to the state, then recurse one level deeper with the updated state.
6. When that recursive call returns, undo the choice — remove it from the state — before trying the next available choice at this level.
7. Once every choice at this level has been tried and undone, return control to the caller, which will likewise undo its own choice.

## The named algorithms

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Backtracking (depth-first search with pruning and undo) | All valid sequences of choices satisfying a set of constraints | Explore the decision tree depth-first, abandoning (pruning) a branch as soon as it violates a constraint, and restoring state on the way back up so siblings start from a clean slate | Worst case O(branching^depth), pruning determines how far below that the real runtime falls |

Backtracking is not a variant of some other named algorithm — it is the technique itself, and its cost is inherently the size of the tree it walks, which is why pruning (step 4 above) is the single biggest lever on performance: a good early-invalidity check can cut off entire subtrees before they're ever built.

## Worked micro-example
Generate all subsets of {1, 2, 3} using backtracking (choose, at each element, to include it or not).

- Start: path = [], index = 0.
- At index 0 (element 1): choose to include it. path = [1]. Recurse to index 1.
  - At index 1 (element 2): choose to include it. path = [1, 2]. Recurse to index 2.
    - At index 2 (element 3): choose to include it. path = [1, 2, 3]. Recurse to index 3 — end of elements, record [1, 2, 3]. Undo: path = [1, 2].
    - Choose to exclude element 3. path = [1, 2]. Recurse to index 3 — end, record [1, 2]. Undo: path = [1, 2] unchanged (nothing was added).
  - Undo including element 2: path = [1].
  - Choose to exclude element 2. path = [1]. Recurse to index 2.
    - Include element 3: path = [1, 3]. Record [1, 3]. Undo: path = [1].
    - Exclude element 3: path = [1]. Record [1]. Undo: path = [1] unchanged.
  - Undo including element 1: path = [].
- Choose to exclude element 1. path = []. (Symmetric exploration follows, eventually recording [2, 3], [2], [3], [].)
- Final recorded subsets: [1,2,3], [1,2], [1,3], [1], [2,3], [2], [3], [] — all 8 subsets of a 3-element set.

## Complexity
Time is bounded by the size of the decision tree actually explored, which in the worst case is O(branching^depth) — for subsets of n elements, that's O(2^n) leaves, each possibly costing O(n) to copy into the answer, giving O(n · 2^n) overall; permutations of n elements cost O(n · n!). Space is O(depth) for the recursion stack plus whatever the current partial state costs to hold, typically O(n) — the output itself, if it must be stored, adds its own size on top.

## Where it breaks
When the input size is large enough that even a well-pruned exponential search is infeasible, backtracking is the wrong tool — that usually signals the problem actually wants a count or an optimum reachable via dynamic programming, not every explicit arrangement. It also doesn't help when there's no meaningful way to prune early (every partial state looks valid until fully built), since then it degenerates into brute force with extra bookkeeping overhead.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Tree recursion (09-trees) | Both recurse into a decision structure, but tree problems combine children's *return values* into one answer for the parent; backtracking cares about the *path itself* (recording it when complete) and explicitly undoes state, which pure tree recursion rarely needs to do. |
| Dynamic programming | Both explore overlapping choices, but DP is for problems that ask for a count, a minimum, or a maximum (where subproblems can be cached and combined) — if the problem wants every actual arrangement rather than a number describing them, it's backtracking. |

## Common traps
- Appending a reference to the mutable path object into the results list instead of a copy — every recorded subset then silently changes as the path is later mutated and undone.
- Forgetting to undo the choice after the recursive call returns, so state from one branch leaks into sibling branches that should have started clean.
- Failing to prune early enough, doing the validity check only when a candidate is fully built instead of the moment it becomes invalid — this wastes enormous amounts of work exploring doomed branches to their full depth.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Combination Sum | Medium | 7 |
| N-Queens | Hard | 6 |
| Word Search | Medium | 5 |
| Sudoku Solver | Hard | 5 |
| Combination Sum II | Medium | 4 |
| Permutations | Medium | 4 |
| Subsets II | Medium | 4 |
| Generate Parentheses | Medium | 3 |
