# Arrays & Hashing

_Pattern id: 01-arrays-hashing · Depends on: (none) · Problems available: 26_

## The one-sentence idea
Trade space for time: a lookup table turns "have I seen this?" or "how many times?" from a scan into a constant-time question.

## How to recognize it
- The problem asks whether an element is a duplicate, or asks for counts or frequencies of elements.
- It asks whether two collections contain the same elements, or the same elements in different amounts.
- You find yourself describing the brute force as "for each element, scan the rest to check something" — a nested loop whose inner loop is only searching or counting.
- The order of the output does not matter, only which elements or how many.
- The alphabet or value range is small and fixed (letters, digits), which hints that a table indexed by that range will work.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **Frequency Map / Counting** | Problem mentions frequency, duplicates, top-k, or counting occurrences | Count elements to find majority, top-k frequent, or sort by frequency |
| **HashMap Design (implementation)** | Problem says “design” or “implement” a map/set without using the language’s built-in one | Back the structure with a bucket array plus chaining, then implement hash, put, get, and remove on top of it |
| **LinkedList with Stack / HashMap** | Problem mentions reverse order processing or “next greater” style operations | Use a stack to handle backward traversal, carry logic, or next greater node |
| **LinkedList with Stack/HashMap** | Problem mentions reverse order processing or “next greater” style operations | Use a stack to handle backward traversal, carry logic, or next greater node |
| **Prefix Sum** | Problem talks about range sum, subarray sum, cumulative sum, or prefix-based queries | Precompute cumulative sums so any subarray or range sum can be answered in O(1) |

## The invariant
The table always holds a summary (presence, count, or last-seen position) of every element processed so far, and nothing else.

## The shape
1. Decide what needs to be looked up later: presence, a count, or a position.
2. Walk the input once, and for each element, first check what the table already says about it.
3. Update the table with the current element (mark it seen, increment its count, or record its index).
4. If the answer can be decided the moment a lookup succeeds or fails, return immediately; otherwise finish the pass and then read off the answer from the table.
5. When comparing two collections, build the table from one and probe it with the other, watching for both "missing" and "wrong count" cases.

## The named algorithms
Most of this pattern is a technique rather than a named algorithm — the skill is recognizing when a table replaces a scan. But a few problems in this pattern are solved by real, named algorithms that skip the table entirely, and one of them (Boyer–Moore Majority Vote) is a genuinely surprising result worth knowing on its own.

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Boyer–Moore Majority Vote Algorithm | The element that appears more than half the time in an array, if one exists | Keep a single "current candidate" and a counter; a matching element increments the counter, a mismatching one decrements it, and when the counter hits zero the candidate is replaced. Because the majority element outnumbers everything else combined, it always survives this cancellation process. No table needed at all. | O(n) time, O(1) space |
| Knuth–Morris–Pratt Algorithm | Whether (and where) one string occurs inside another | Precomputes, for the pattern being searched, how far to skip ahead on a mismatch by reusing information about the pattern's own repeated prefixes, so the search never re-examines a character it has already matched | O(n + m) time, where n and m are the lengths of the text and pattern; O(m) space |
| Z Algorithm | For every position in a string, the length of the longest substring starting there that matches the string's own prefix | Maintains a window of the farthest-reaching prefix match found so far and reuses previously computed values inside that window instead of recomparing characters from scratch | O(n) time, O(n) space |

## Worked micro-example
Input: array `[4, 1, 2, 4, 3]`. Task: find the first element that repeats.
Start with an empty "seen" table.
- Index 0, value 4: not in seen. Add 4 to seen. Seen = {4}.
- Index 1, value 1: not in seen. Add 1. Seen = {4, 1}.
- Index 2, value 2: not in seen. Add 2. Seen = {4, 1, 2}.
- Index 3, value 4: 4 is already in seen — this is the first repeat. Stop.
Answer: 4. A brute-force approach would have compared index 3 against every earlier index; the table let each comparison happen in one lookup instead of a scan back through the array.

## Complexity
Typical time is O(n), driven by one pass over the input where each lookup and insert into the table costs O(1) on average. Typical space is O(n) or O(k) where k is the size of the value alphabet (e.g., 26 for lowercase letters), driven by how many distinct entries the table must hold.

## Where it breaks
- The answer depends on order or position relative to neighbors (e.g., the longest run of consecutive equal elements) — a table alone discards position information unless you deliberately store it.
- The data is a stream too large to hold in memory, so an exact table is not feasible and approximate structures are needed instead.
- The problem needs range queries (sum or count over an interval) rather than point lookups — a table answers "is X present" but not "how many values lie between A and B" efficiently.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Two Pointers | Two Pointers needs sorted or symmetric structure and exploits position; Arrays & Hashing ignores position and only cares about presence/count. |
| Sliding Window | Sliding Window also often uses a table internally, but the question is about a *contiguous* range, not the whole collection. |
| Binary Search | If the input is sorted and you're checking existence, binary search may beat a hash table on space at the cost of needing sorted order. |

## Common traps
- Using a list where a set or map would do, silently keeping an O(n) lookup inside what looks like an O(1) step.
- Counting characters or elements while forgetting the alphabet is bounded, which would let you use a fixed-size array instead of a general hash map.
- Assuming presence is enough when the problem actually needs a count (e.g., "anagram" needs matching counts per character, not just matching characters).

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Two Sum | Easy | 6 |
| Valid Anagram | Easy | 6 |
| Majority Element | Easy | 4 |
| Longest Consecutive Sequence | Medium | 6 |
| Top K Frequent Elements | Medium | 5 |
| Majority Element II | Medium | 4 |
| Repeated String Match | Medium | 4 |
| String to Integer (atoi) | Medium | 4 |
