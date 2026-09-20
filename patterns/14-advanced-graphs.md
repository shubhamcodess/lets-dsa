# Advanced Graphs

_Pattern id: 14-advanced-graphs · Depends on: 13-graphs, 11-heap-top-k · Problems available: 8_

## The one-sentence idea
Once edges carry weights or costs, plain BFS stops guaranteeing the shortest answer — this pattern is the family of algorithms built to handle weighted and structured graphs: cheapest paths, cheapest ways to connect everything, and cycle detection across merging groups.

## How to recognize it
- Edges explicitly carry weights, costs, times, or distances rather than all being equal.
- It asks for the cheapest path between two points, or the minimum cost to connect every node in a network together.
- It asks to detect a cycle, or check connectivity, as elements are merged together one operation at a time (union-find territory).
- It mentions a limit on the number of stops, edges, or hops allowed along the way, on top of minimizing cost.
- It asks for an ordering with additional structure beyond a simple topological sort — for example, counting how many valid orderings exist, or finding the lexicographically smallest one.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **Bellman-Ford** | Problem mentions “negative weights, cycles, or cost minimization with negative edges” | Relax all edges V-1 times → detect negative cycles |
| **Dijkstra (Weighted)** | Problem mentions “weighted edges, shortest path, or minimum distance in weighted graph” | Use priority queue → relax edges → track shortest distances |
| **Floyd-Warshall** | Problem mentions “all-pairs shortest paths, matrix, or city connectivity between any two nodes” | DP over adjacency matrix → shortest paths between all pairs of nodes |
| **MST / Union-Find** | Problem mentions “minimum cost to connect all nodes, redundant connections, union-find required” | Use Kruskal’s / Prim’s algorithm or Union-Find → find MST, minimum cost connections, or detect cycles |

## The invariant
Once a node is finalized (its shortest distance is settled and will never be revisited), that distance is optimal and will never change again — everything explored afterward can only be equal or worse.

## The shape
**Dijkstra's algorithm (cheapest path from one source, non-negative weights):**
1. Set the source's distance to zero and every other node's distance to infinity.
2. Put the source into a min-priority-queue, keyed by current known distance.
3. Repeatedly pop the node with the smallest distance from the queue. If it's already been finalized, skip it.
4. Finalize that node — its popped distance is now guaranteed optimal.
5. For each of its neighbors, compute the distance through this node; if that's better than the neighbor's current known distance, update it and push the neighbor into the queue with the new distance.
6. Repeat until the queue is empty; every node's finalized distance is the shortest path from the source.

**Bellman-Ford (cheapest path from one source, tolerates negative weights, detects negative cycles):**
1. Set the source's distance to zero and every other node's distance to infinity.
2. Repeat, for a number of rounds equal to one less than the number of nodes: for every edge, check if going through its start node gives a shorter distance to its end node, and update if so.
3. After enough rounds, every reachable node has its true shortest distance (since a shortest simple path visits at most V−1 edges).
4. Run one more full pass over all edges; if any distance can still be improved, a negative-weight cycle exists that makes "shortest path" undefined.

**Kruskal's algorithm (minimum spanning tree, edge-focused):**
1. Sort every edge by weight, ascending.
2. Go through edges in that order; for each edge, check whether its two endpoints are already connected (via union-find).
3. If they're not already connected, add the edge to the spanning tree and union the two endpoints together.
4. If they're already connected, adding this edge would create a cycle — skip it.
5. Stop once the tree has exactly (number of nodes − 1) edges — every node is now connected using minimum total weight.

**Prim's algorithm (minimum spanning tree, node-focused):**
1. Start from any node, and mark it as part of the growing tree.
2. Put all edges leaving that node into a min-priority-queue, keyed by weight.
3. Repeatedly pop the cheapest edge; if it leads to a node not yet in the tree, add that node to the tree and add all of its outgoing edges to the queue.
4. If the popped edge leads to a node already in the tree, discard it (it would create a cycle).
5. Repeat until every node has joined the tree.

**Union-Find with path compression and union by rank (tracking merging groups):**
1. Start with every element as its own separate group (its own parent).
2. To find which group an element belongs to, follow parent pointers up to the representative (root) of its group — and while doing so, point every node visited along the way directly at that root (path compression), so future lookups are faster.
3. To union two elements, find each one's group root; if the roots differ, attach the smaller/shallower tree's root under the larger/deeper tree's root (union by rank or size), keeping the overall structure flat.
4. Two elements are in the same group exactly when they share the same root.

## The named algorithms

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Dijkstra's algorithm | Shortest path from a single source to all nodes, with non-negative edge weights | A priority queue always finalizes the currently-closest unfinalized node next, and once finalized a node's distance can never improve, since all other edges only add non-negative cost | O((V + E) log V) with a binary heap |
| Bellman-Ford | Shortest path from a single source, tolerating negative weights, and detecting negative-weight cycles | Relax every edge repeatedly; V−1 rounds suffice because a shortest simple path has at most V−1 edges, and a possible V-th improving round reveals a negative cycle | O(V · E) |
| Kruskal's algorithm | Minimum spanning tree — the cheapest set of edges connecting all nodes with no cycles | Greedily take the globally cheapest edge that doesn't create a cycle, checked efficiently with union-find | O(E log E) for sorting edges |
| Prim's algorithm | Minimum spanning tree, grown outward from a starting node | Greedily extend the current tree with the cheapest edge leaving it to a node not yet included | O(E log V) with a binary heap |
| Union-Find (Disjoint Set Union) with path compression | Tracks which elements belong to the same group as merges happen, and detects when a merge would form a cycle | Path compression flattens the tree on every lookup; union by rank/size keeps trees shallow — together they make near-constant-time operations | O(α(n)) per operation (effectively constant), α = inverse Ackermann function |

Dijkstra and Bellman-Ford both solve single-source shortest paths but trade off differently: Dijkstra is faster but breaks on negative weights, Bellman-Ford is slower but handles them and can prove none exist. Kruskal and Prim both build a minimum spanning tree but grow it differently — Kruskal thinks in terms of the globally sorted edge list, Prim thinks in terms of a single tree expanding outward — and they end up needing different supporting structures (union-find for Kruskal, a priority queue over frontier edges for Prim). Union-Find underlies Kruskal directly and shows up independently in any problem about merging groups and detecting when a merge closes a cycle.

## Worked micro-example
**Dijkstra** on a small weighted graph: A→B (weight 4), A→C (weight 1), C→B (weight 1), B→D (weight 1), C→D (weight 5). Find shortest distances from A.

- Distances: A=0, B=∞, C=∞, D=∞. Queue: [(0, A)].
- Pop (0, A). Finalize A at 0. Relax neighbors: B via A = 0+4=4 (better than ∞, update B=4); C via A = 0+1=1 (update C=1). Queue: [(1, C), (4, B)].
- Pop (1, C). Finalize C at 1. Relax neighbors: B via C = 1+1=2 (better than current 4, update B=2); D via C = 1+5=6 (update D=6). Queue: [(2, B), (4, B) stale, (6, D)].
- Pop (2, B). Finalize B at 2. Relax neighbor: D via B = 2+1=3 (better than 6, update D=3). Queue: [(3, D), (4, B) stale, (6, D) stale].
- Pop (3, D). Finalize D at 3.
- Pop (4, B): B is already finalized, skip. Pop (6, D): D is already finalized, skip.
- Final distances: A=0, B=2 (via C), C=1, D=3 (via C then B) — notice the direct A→B edge of weight 4 was correctly passed over in favor of the cheaper A→C→B route of total weight 2.

**Union-Find** merging groups from edges (1,2), (3,4), (2,3): 
- Start: each of 1,2,3,4 is its own root.
- Union(1,2): roots differ (1 and 2), attach one under the other. Group: {1,2}.
- Union(3,4): roots differ (3 and 4), attach one under the other. Group: {3,4}.
- Union(2,3): find root of 2 (→1's group), find root of 3 (→3's group), roots differ, merge them. All of {1,2,3,4} now share one root — one connected group. A later edge like (1,4) would find both already sharing a root, signaling a cycle if added again.

## Complexity
Dijkstra costs O((V + E) log V) with a binary heap, since every node is popped once and every edge can trigger one heap push, each costing O(log V). Bellman-Ford costs O(V · E) because it makes V−1 full passes over every edge. Kruskal costs O(E log E) dominated by sorting the edges, with near-constant-time union-find operations after that. Prim costs O(E log V), similar to Dijkstra, since it's also a priority-queue-driven greedy expansion. Union-Find alone costs O(α(n)) per operation — so close to constant that it's treated as O(1) in practice — where α is the inverse Ackermann function, growing so slowly it never exceeds 5 for any input size that could exist in practice.

## Where it breaks
Dijkstra fails silently and incorrectly on negative edge weights — it finalizes nodes greedily under the assumption that no later, cheaper path can appear, which a negative edge can violate; Bellman-Ford is the fallback in that case, at a real cost in speed. MST algorithms (Kruskal, Prim) only apply to undirected, connected graphs where "connect everything as cheaply as possible" is well-defined — they don't apply to directed graphs (that's a different problem, minimum arborescence) or to shortest-path questions between two specific nodes rather than connecting all nodes. Union-Find without path compression or union by rank degrades toward a plain linked list under repeated unbalanced merges, losing its near-constant-time guarantee.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Plain BFS (13-graphs) | BFS finds shortest paths only when every edge costs the same; the instant weights differ, BFS's level-by-level guarantee no longer corresponds to cheapest cost, and Dijkstra (or Bellman-Ford, for negative weights) is required instead. |
| Kruskal vs. Prim (each other) | Both build a minimum spanning tree with the identical final cost, but Kruskal is easier when the edge list is naturally available and sorted once; Prim is easier when the graph is given as an adjacency list and you'd rather grow a frontier than pre-sort all edges. |
| Topological sort with counting/DP | A weighted DAG shortest-path problem can look like a topological-sort problem, but the moment edge costs matter for what "best" means, you're combining topological order with a relaxation step, not merely producing any valid order. |

## Common traps
- Running Dijkstra on a graph with negative edge weights, silently producing a wrong (too-optimistic) answer instead of erroring — Dijkstra has no built-in way to detect this violation of its own assumption.
- Implementing union-find without path compression or union by rank/size, letting merge chains degrade toward a linked list and turning near-constant operations into linear ones.
- Forgetting to skip a popped node in Dijkstra if it's already been finalized — since the same node can be pushed onto the priority queue multiple times with different (stale) distances before the best one is popped.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Alien Dictionary | Hard | 5 |
| Cheapest Flights Within K Stops | Medium | 4 |
| Accounts Merge | Medium | 3 |
| Network Delay Time | Medium | 2 |
| Swim in Rising Water | Hard | 2 |
| Min Cost to Connect All Points | Medium | 1 |
| Number of Islands II | Hard | 1 |
| Reconstruct Itinerary | Hard | 1 |
