# Trees (DFS & BFS)

_Pattern id: 09-trees · Depends on: 05-stack · Problems available: 36_

## The one-sentence idea
Recursion mirrors the tree's own structure: decide what each node needs from its children, and what it hands back to its parent, and the whole tree gets solved one subtree at a time.

## How to recognize it
- The input is explicitly a binary tree or an n-ary tree (nodes with `left`/`right` or a list of `children`).
- The question mentions depth, height, path, ancestor, or level.
- It asks to validate a property of the whole structure (is it balanced, is it a valid BST, are two trees the same) — properties that depend on every subtree being correct.
- It asks to build a tree from a description (traversal orders, a string, a list) or to serialize one into a string.
- It asks for something "level by level" — a strong signal for breadth-first traversal specifically, rather than depth-first.

## The invariant
Each recursive call returns a correct answer for its whole subtree, on the assumption that the calls it made on its children already did.

## The shape
For depth-first approaches:
1. Define what a single call should return for the subtree rooted at the node it's given (a boolean, a height, a sum, a list — whatever the parent will need).
2. Handle the base case: what an empty (null) subtree returns.
3. Recurse into the left and/or right children (or all children, for n-ary trees) to get their results.
4. Combine the children's results with the current node's own value into the result for this subtree.
5. Return that combined result to the caller.
6. If the problem also needs a value not naturally passed upward (like a running maximum found anywhere in the tree), thread it through a value that lives outside the return channel — an accumulator captured by the recursive calls, updated as a side effect while the "official" return value still flows bottom-up.

For breadth-first approaches:
1. Put the root into a queue.
2. While the queue is not empty, record how many nodes are currently in it — that count is exactly one level.
3. Pop that many nodes, process each, and push each one's children onto the queue.
4. Repeat until the queue empties; each pass through step 2–3 corresponds to one level of the tree.

## The named algorithms

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Depth-first traversal (preorder / inorder / postorder) | Visits every node, ordering the visit relative to when children are visited | Recurse into children before, between, or after processing the current node; which order you pick encodes different information (inorder on a BST yields sorted order) | O(n) time, O(h) space for the call stack, h = height |
| Breadth-first traversal (level order) | Visits nodes level by level, nearest to the root first | A queue naturally holds "the frontier" — everything at the current distance from the root — so processing it in batches separates levels | O(n) time, O(w) space, w = maximum width of the tree |

Preorder, inorder, and postorder are the three depth-first orderings, distinguished only by when the current node is processed relative to its children (before both, between them, after both). Level-order (BFS) is the width-first alternative and is what "level by level" or "minimum depth" questions are really asking for, since DFS would need to explore an entire deep branch before comparing it to a shallow one.

## Worked micro-example
Tree:
```
        1
       / \
      2   3
     /
    4
```
**DFS (postorder, computing height):**
- Call on node 4: no children, returns height 1.
- Call on node 2: recurse left → node 4 returns 1; no right child, treated as height 0. Node 2's height = 1 + max(1, 0) = 2.
- Call on node 3: no children, returns height 1.
- Call on node 1: left subtree (node 2) returned 2; right subtree (node 3) returned 1. Node 1's height = 1 + max(2, 1) = 3.
- Final answer: height 3.

**BFS (level order):**
- Queue: [1]. Level size = 1. Pop 1, record it, push its children → queue: [2, 3]. Level 1 output: [1].
- Level size = 2. Pop 2, push its child 4 → queue: [3, 4]. Pop 3, no children → queue: [4]. Level 2 output: [2, 3].
- Level size = 1. Pop 4, no children → queue: []. Level 3 output: [4].
- Queue empty, done. Levels: [[1], [2, 3], [4]].

## Complexity
Both traversal styles visit every node exactly once, so time is O(n) where n is the number of nodes. Space differs by shape: DFS space is O(h), the height of the tree, because that's the deepest the recursive call stack goes — O(log n) for a balanced tree, O(n) for a completely skewed one. BFS space is O(w), the widest level of the tree, which can also reach O(n) for a wide, shallow tree (e.g., a complete tree's bottom level holds roughly half the nodes).

## Where it breaks
The recursive mirroring breaks down when a node's correct answer genuinely depends on information from *outside* its own subtree (siblings, ancestors, or the tree's global structure beyond what fits in an accumulator) — those problems usually need extra parameters threaded down from the root (a range, a running sum, a boolean) rather than pure bottom-up composition. Very deep, unbalanced trees can also blow the recursion (call) stack in languages without tail-call optimization, favoring an explicit-stack iterative rewrite.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Graphs (13-graphs) | A tree is a connected graph with no cycles and exactly one path between any two nodes — if the input can have cycles, multiple parents, or is described as generic nodes-and-edges rather than a rooted hierarchy, it's graphs, not trees. |
| Backtracking (12-backtracking) | Both recurse and both "undo" state on the way out, but trees combine children's *results* into a value for the parent; backtracking explores a decision tree to enumerate *all* valid sequences of choices, usually with no meaningful "return value" beyond having recorded a path. |

## Common traps
- Validating a BST by comparing each node only to its immediate parent, instead of propagating a valid `(low, high)` range down from the root — this misses violations from a grandparent or higher ancestor.
- Confusing depth (distance from the root down to a node) with height (distance from a node down to its deepest leaf) — they are measured in opposite directions and many bugs come from silently swapping them.
- Forgetting the null/empty base case, causing a crash on leaves, or returning the wrong "neutral" value (e.g., returning 0 instead of `-infinity` when a missing child shouldn't count as a candidate maximum).

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Diameter of Binary Tree | Easy | 6 |
| Maximum Depth of Binary Tree | Easy | 6 |
| Same Tree | Easy | 6 |
| Lowest Common Ancestor of a Binary Search Tree | Medium | 7 |
| Binary Tree Level Order Traversal | Medium | 6 |
| Construct Binary Tree from Preorder and Inorder Traversal | Medium | 6 |
| Kth Smallest Element in a BST | Medium | 6 |
| Validate Binary Search Tree | Medium | 6 |
