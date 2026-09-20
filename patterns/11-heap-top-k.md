# Heap / Top-K

_Pattern id: 11-heap-top-k · Depends on: 01-arrays-hashing · Problems available: 9_

## The one-sentence idea
You rarely need the whole thing sorted — a heap of size k keeps only the candidates that can still possibly win, and discards everything else the instant it's beaten.

## How to recognize it
- The question asks for the k largest, k smallest, or k most frequent elements.
- It asks for a running median, or any statistic that must be answered repeatedly as elements arrive one at a time (a stream).
- It asks to merge several already-sorted sources into one sorted result.
- It involves scheduling or repeatedly picking "the best available option right now" and putting it back with a changed priority afterward (like a cooldown or a task queue).
- The phrase "k" appears attached to a comparison ("kth largest", "top k", "k closest") rather than needing every element ranked.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **Implementation of Heap** | Design Priority Queue | Design heap |
| **Merge K Sorted** | Problem mentions merging sorted arrays/lists or finding K smallest/largest pairs across arrays | Use min-heap to merge multiple sorted arrays/lists efficiently |
| **Top-K Elements** | Problem mentions top k, kth largest/smallest, median, or maintaining running extremes | Use min-heap for top-k largest, max-heap for top-k smallest → maintain heap of size k |

## The invariant
The heap holds the best k candidates seen so far, and its root (top) is always the weakest of those k — the one that gets evicted the instant something better shows up.

## The shape
1. Decide what "best" means for this problem, and size the heap to hold exactly k elements (or two heaps, for a median).
2. For each new element, if the heap has fewer than k elements, add it directly.
3. If the heap already has k elements, compare the new element to the heap's root (the current worst of the best-k). If the new element is better, remove the root and insert the new element; otherwise discard the new element — it can't make the top-k.
4. After processing everything, the heap contains exactly the top-k elements, with the root being the kth-best.
5. For a running median with two heaps: keep a max-heap holding the smaller half of numbers seen and a min-heap holding the larger half, always rebalancing after each insert so the two halves differ in size by at most one — the median is then either the root of the larger heap, or the average of both roots.
6. For merging k sorted sources: seed the heap with the first element from each source; repeatedly pop the smallest, output it, and push the next element from the same source it came from, until all sources are exhausted.

## The named algorithms

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Binary heap (priority queue) operations | Maintains a collection where the minimum (or maximum) element is always retrievable and removable quickly | A complete binary tree stored in an array, kept so every parent is smaller (or larger) than its children — "sift up" and "sift down" restore this after insert/remove | Insert/pop: O(log n); peek: O(1) |
| Two-heap median maintenance | The running median of a stream, updatable after each insertion | Split the stream into a max-heap of the lower half and a min-heap of the upper half, keeping their sizes balanced so the median sits at one or both roots | O(log n) per insertion, O(1) per median query |
| K-way merge | Merges k already-sorted lists into one sorted output | A heap of size k, holding one "current" candidate from each list, always exposes the global next-smallest element in O(log k) | O(n log k) time, n = total elements, k = number of lists |

The binary heap itself is the workhorse — nearly every problem in this pattern is "maintain a heap of the right size with the right comparator." The two variants above (two-heap median, k-way merge) are named techniques built directly on top of that one structure, each exploiting a different property of "the root is always the extreme."

## Worked micro-example
Find the 3 largest numbers in the stream: 5, 1, 9, 3, 7, 2 (k = 3, using a min-heap of size k so the root is the smallest of the current top-3).

- Push 5. Heap: [5]. (size < 3, keep filling)
- Push 1. Heap: [1, 5]. (size < 3, keep filling)
- Push 9. Heap: [1, 5, 9]. (size = 3 now, root = 1)
- Next, 3: compare to root 1, the current worst of the top-3. 3 > 1 means 3 beats the current worst, so evict 1, insert 3. Heap: [3, 5, 9], root = 3.
- Next, 7: compare to root 3. 7 > 3, evict 3, insert 7. Heap: [5, 7, 9], root = 5.
- Next, 2: compare to root 5. 2 < 5, so 2 cannot beat the current worst of the top-3 — discard 2. Heap unchanged: [5, 7, 9].
- Final heap contents: {5, 7, 9} — the 3 largest numbers seen, with 5 (the root) being the smallest of them, i.e. the 3rd largest overall.

## Complexity
Each insertion or removal from a heap of size k costs O(log k), so processing n elements while maintaining a top-k heap costs O(n log k) time — notably cheaper than sorting everything (O(n log n)) whenever k is much smaller than n. Space is O(k), since the heap only ever holds k elements regardless of how many total elements are processed; a full sort would need O(n) space to hold everything.

## Where it breaks
If k is close to n, a size-k heap offers little advantage over just sorting the whole collection — the log k factor approaches log n and the bookkeeping overhead isn't worth it. It also doesn't help when you need the *full* order of all elements, not just the extremes, or when elements need to be looked up and updated by identity rather than compared purely by priority (that calls for an indexed priority queue or a different structure entirely).

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Sorting | Sorting gives you every element in order for O(n log n); a top-k heap gives you only the extremes for O(n log k) — reach for sorting only when the full order is actually needed. |
| Quickselect (partition-based selection) | Both find the kth largest/smallest, but quickselect works on a fixed, static array in O(n) average time; a heap is the right choice specifically when data arrives as a stream or the top-k must be maintained incrementally. |

## Common traps
- Inverting the heap type: using a max-heap when a min-heap was needed (or vice versa) — "k largest" needs a *min*-heap of size k (so the smallest of the current best-k sits on top, ready to be evicted), which trips people up because it feels backwards at first.
- Sorting the entire input when a size-k heap would answer the question with far less work and memory.
- Forgetting to rebalance the two-heap median structure after every insertion, letting the size difference between the two halves grow past one and silently corrupting the median.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Kth Largest Element in a Stream | Easy | 4 |
| Find Median from Data Stream | Hard | 6 |
| Kth Largest Element in an Array | Medium | 4 |
| Task Scheduler | Medium | 4 |
| Design Twitter | Medium | 2 |
| K Closest Points to Origin | Medium | 2 |
| Last Stone Weight | Easy | 1 |
| Sort Characters By Frequency | Medium | 1 |
