# Graphs

_Pattern id: 13-graphs · Depends on: 09-trees · Problems available: 27_

## The one-sentence idea
A graph is a tree that's allowed to have cycles and multiple paths between nodes — everything from trees still applies, but now you must actively remember what you've already visited, or you'll loop forever.

## How to recognize it
- The problem describes a grid or matrix of cells, and asks about connected regions, islands, or areas that can be reached from one another (land/water, distinct colors, connected zones).
- It describes nodes and edges directly, or a relationship implying them: prerequisites, connections, friendships, routes between cities.
- It asks for the shortest path, or minimum number of steps, in a graph where every edge costs the same (unweighted).
- It asks about cycles, or about ordering things so that dependencies come before what depends on them.
- It asks whether every node can reach every other node, or how many separate groups the nodes fall into.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **BFS (Unweighted Path)** | Problem mentions “shortest path, level-order traversal, or unweighted distance” | Standard BFS → track distance/levels → queue-based traversal → multi-source if needed |
| **BFS Pattern** | Problem mentions “shortest path, level-order traversal, or unweighted distance” | Standard BFS → track distance/levels → queue-based traversal → multi-source if needed |
| **DFS (Connectivity)** | Problem mentions “connected components, islands, cycles, safe states, bipartite check, bridges, articulation points, or connectivity check” | DFS recursion or stack → track visited → identify connected components or detect cycles |
| **Topological Sort** | Problem mentions “ordering tasks, course prerequisites, dependency chains, build order, or cycle in directed graph” | DFS postorder or BFS (Kahn’s algorithm) → order nodes respecting dependencies |

## The invariant
Every node is enqueued (or recursed into) at most once — visited status is marked at the moment a node is *discovered* and scheduled for processing, not at the moment it's actually processed, or the same node can enter the frontier multiple times.

## The shape
**Breadth-first search (shortest path in unweighted graphs, level-by-level spread):**
1. Put the starting node(s) into a queue, and mark them visited immediately.
2. While the queue is not empty, pop a node and process it.
3. For each neighbor of that node, if it hasn't been visited yet, mark it visited right away and push it onto the queue.
4. Repeat until the queue is empty — nodes come out in order of increasing distance from the start, which is exactly why BFS finds shortest paths on unweighted graphs.

**Depth-first search (exploring as far as possible before backing up):**
1. Start at a node, mark it visited.
2. For each unvisited neighbor, recurse into it (or push it onto an explicit stack) before returning to try the next neighbor.
3. When a node has no more unvisited neighbors, back out to whichever node called into it.
4. This naturally explores one whole branch before touching a sibling branch — useful for connectivity, cycle detection, and problems where the "path so far" matters.

**Topological sort (ordering nodes so every edge points from earlier to later, Kahn's algorithm):**
1. Count, for every node, how many edges point *into* it (in-degree).
2. Put every node with in-degree zero into a queue — these have no unmet dependencies.
3. Pop a node from the queue, add it to the output order, and for each edge leaving it, decrement the in-degree of the node it points to.
4. Whenever a neighbor's in-degree drops to zero, push it onto the queue.
5. Repeat until the queue is empty. If every node made it into the output order, a valid ordering exists; if some nodes never reached in-degree zero, the graph has a cycle and no valid ordering exists.

## The named algorithms

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Breadth-first search (BFS) | Shortest path (in edge count) from a source to all reachable nodes, in an unweighted graph | Explore the frontier one full layer at a time using a queue, so nodes are finished in strictly increasing order of distance | O(V + E) time, O(V) space |
| Depth-first search (DFS) | Reachability, connected components, cycle detection, and orderings that depend on exploring one path fully before trying another | Recurse (or use an explicit stack) to go as deep as possible before backtracking, marking nodes visited on entry | O(V + E) time, O(V) space (recursion stack) |
| Kahn's algorithm (BFS-based topological sort) | A linear ordering of nodes in a directed acyclic graph such that every edge goes from earlier to later, or detects that no such ordering exists | Repeatedly peel off nodes with no remaining unmet dependencies (in-degree zero), which is exactly the BFS frontier of "currently unblocked" nodes | O(V + E) time, O(V) space |

BFS and DFS are the two ways to systematically visit a graph, differing only in which data structure holds the frontier (queue vs. stack/recursion) — that single difference is what makes BFS the right tool for shortest unweighted paths and DFS the natural fit for exhaustive exploration and cycle checks. Kahn's algorithm is BFS applied to a specific derived quantity (in-degree) rather than to the raw adjacency directly, which is why it's presented as its own named technique even though the traversal engine underneath is BFS.

## Worked micro-example
**BFS shortest path** on a small unweighted graph: A–B, A–C, B–D, C–D, D–E. Find the shortest path from A to E.

- Queue: [A], visited: {A}, distance: {A: 0}.
- Pop A. Neighbors B, C — both unvisited. Mark visited, set distance 1. Queue: [B, C].
- Pop B. Neighbor D — unvisited. Mark visited, distance 2. Queue: [C, D].
- Pop C. Neighbor D — already visited, skip. Queue: [D].
- Pop D. Neighbor E — unvisited. Mark visited, distance 3. Queue: [E].
- Pop E. No unvisited neighbors. Queue empty.
- Shortest distance A to E is 3 (A→B→D→E, or equivalently via C).

**Kahn's topological sort** on courses with prerequisites: edges 1→2, 1→3, 2→4, 3→4 (meaning "1 before 2", etc.).

- In-degrees: 1:0, 2:1, 3:1, 4:2.
- Queue starts with nodes at in-degree 0: [1].
- Pop 1, output [1]. Decrement in-degree of 2 (→0) and 3 (→0). Both now qualify: queue becomes [2, 3].
- Pop 2, output [1, 2]. Decrement in-degree of 4 (→1). Not zero yet, stays out of queue. Queue: [3].
- Pop 3, output [1, 2, 3]. Decrement in-degree of 4 (→0). Now qualifies: queue: [4].
- Pop 4, output [1, 2, 3, 4]. Queue empty.
- All 4 nodes made it into the order — valid topological order: 1, 2, 3, 4.

## Complexity
Both BFS and DFS visit every node once and examine every edge once, giving O(V + E) time, where V is the number of nodes and E the number of edges — for a grid of size m×n, V and E are both proportional to m·n, so it's often written as O(m·n). Space is O(V) for the visited set plus whatever the frontier structure holds (the queue for BFS, the call stack or explicit stack for DFS) — in the worst case, a wide graph can have a queue holding nearly all of V, and a deep graph can have a recursion stack nearly V deep.

## Where it breaks
BFS's shortest-path guarantee only holds when every edge costs the same — as soon as edges carry different weights or costs, BFS can return a path with more hops but lower total cost than the true shortest one, and a weighted algorithm is needed instead (see 14-advanced-graphs). DFS-based approaches can also overflow the call stack on very deep or very large graphs, favoring an iterative rewrite with an explicit stack.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Trees (09-trees) | A tree is a special graph with no cycles and exactly one path between any two nodes; if the input can revisit nodes, have multiple parents, or form loops, treat it as a graph and track visited state explicitly — trees never need to. |
| Advanced graphs (14-advanced-graphs) | If every edge is unweighted (or weights are irrelevant to the question), plain BFS/DFS/Kahn's suffice; the moment edges carry costs and the question asks for a *cheapest* path or connection, it moves into weighted territory. |

## Common traps
- Marking a node visited when it's *dequeued* rather than when it's *enqueued* — this lets the same node enter the queue multiple times through different paths, wasting work and sometimes producing wrong distances.
- Treating an undirected edge as one-directional — an edge between A and B in an undirected graph must be traversable both A→B and B→A, and forgetting to add both directions to the adjacency structure silently breaks connectivity.
- Re-running a full traversal from scratch for every query instead of computing connectivity or distances once and reusing the result, when the underlying graph doesn't change between queries.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Flood Fill | Easy | 4 |
| Number of Islands | Medium | 7 |
| Course Schedule | Medium | 6 |
| Rotting Oranges | Medium | 6 |
| Clone Graph | Medium | 5 |
| Course Schedule II | Medium | 4 |
| Word Ladder | Hard | 4 |
| Graph Valid Tree | Medium | 3 |
