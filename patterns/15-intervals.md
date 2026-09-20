# Intervals

_Pattern id: 15-intervals · Depends on: 02-two-pointers · Problems available: 6_

## The one-sentence idea
Sort the intervals by one endpoint, then walk through them once, deciding overlap by comparing only the current interval to the one you just finalized.

## How to recognize it
- The input is a list of pairs, each representing a start and an end (a range, a booking, a time window).
- The question asks you to merge, insert, count, or remove overlapping ranges.
- The scenario is phrased as scheduling: meeting rooms, calendars, bookings, flight times, or "can a person attend both."
- There is no need to look more than one interval back at a time — the problem is about pairwise overlap along a line, not about relationships between far-apart ranges.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **DP on Intervals** | Problem mentions “intervals, subarray partitions, merging cost, or burst balloons” | Track optimal solutions for subarrays/intervals → matrix chain, merging, or balloon burst patterns |
| **Intervals & Reach** | Problem mentions “maximum non-overlapping intervals, tasks, meetings, jump to end, minimum steps, or cover intervals” | Sort intervals or extend reach as far as possible from current position → maximize tasks done / minimize steps |

## The invariant
After sorting and processing up through the current interval, every interval before it in the scan is already fully merged, finalized, and will never change again.

## The shape
1. Decide which endpoint to sort by. For merging or overlap counting, sort by start. For "does this fit before a deadline" problems, sort by end.
2. Initialize a "current" interval (or a small structure like a min-heap of end times) with the first interval after sorting.
3. Scan the rest in sorted order. For each new interval, compare its start against the end of the current interval (or the front of the heap).
4. If the new interval overlaps, merge it in — extend the end if needed — instead of starting a new interval.
5. If it does not overlap, close out the current interval (emit it, or in the meeting-rooms variant, note that a new room is needed), and make the new interval the current one.
6. Continue until the input is exhausted, then close out whatever interval is still open.
Sorting first is what makes a single left-to-right pass sufficient: once ordered, an interval can only ever conflict with its immediate predecessor in the merged sequence, never with something further back.

## The named algorithms
This pattern is a technique, not a named algorithm family. There is no textbook-named "interval algorithm" the way there is a Kadane's or a Dijkstra's — every problem in this bucket is a variation on "sort, then sweep," and the skill is picking the right sort key and the right merge rule for the specific question, not recalling a named procedure.

## Worked micro-example
Take intervals [1,4], [2,3], [6,8]. Sort by start — they're already sorted.
Start with current = [1,4]. Next is [2,3]: its start (2) is less than or equal to current's end (4), so they overlap. Merge: current stays [1,4] since 4 is already bigger than 3's end.
Next is [6,8]: its start (6) is greater than current's end (4), so no overlap. Close out [1,4] as a finished merged interval, and set current = [6,8].
No more intervals. Close out [6,8].
Result: [1,4] and [6,8] are the merged intervals.

## Complexity
Time is dominated by the sort: O(n log n) for n intervals, since the sweep itself is a single O(n) pass. Space is O(n) for the output (or O(log n) to O(n) for the sort's own overhead), plus O(k) if a heap of active end times is used for room-counting variants, where k is the maximum number of overlapping intervals at once.

## Where it breaks
It breaks when overlap is not the whole story — for example, when you must choose a subset of intervals to maximize some weighted value rather than just merge or count them. That shifts the problem into greedy-with-proof or DP territory, because now the choice of which interval to keep can affect which future intervals are still available, and a single sweep with a fixed merge rule can't capture that trade-off.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Greedy (16-greedy) | Interval problems that ask to *select the maximum number of non-overlapping intervals* are really greedy-by-end-time; pure interval-merging never has to choose which intervals to drop. |
| Sliding window | Both involve a moving boundary over ordered data, but sliding window operates over one array of elements with a size/sum condition, not over explicit start/end pairs. |
| Sweep-line for geometry | Some interval problems (like the hard "minimum interval to include each query") extend the sweep with a heap, which starts to resemble a geometric sweep-line — the giveaway is that it needs an ordered structure of active elements, not just a single "current" interval. |

## Common traps
- Sorting by the end endpoint when the problem needs the start (or vice versa) — the wrong sort key silently breaks the single-pass guarantee.
- Off-by-one errors on whether touching endpoints (e.g., an interval ending at 4 and one starting at 4) count as overlapping — this depends on whether ranges are inclusive, and problems differ.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Meeting Rooms | Easy | 3 |
| Merge Intervals | Medium | 6 |
| Insert Interval | Medium | 4 |
| Non-overlapping Intervals | Medium | 4 |
| Meeting Rooms II | Medium | 3 |
| Minimum Interval to Include Each Query | Hard | 1 |
