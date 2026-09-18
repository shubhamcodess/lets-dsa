# Tries

_Pattern id: 10-tries · Depends on: 09-trees · Problems available: 7_

## The one-sentence idea
A tree keyed by character, where every path down from the root spells out a prefix, so questions about shared prefixes cost the length of a word instead of the size of the whole dictionary.

## How to recognize it
- The problem asks for prefix search, autocomplete, or "starts with" queries.
- Many words or strings need to be queried repeatedly against one fixed dictionary — a strong hint that preprocessing that dictionary once pays off across queries.
- Wildcard matching against a set of stored words (a `.` that can match any character, checked against previously inserted words).
- The task is explicitly to "design" a data structure that supports insert, search, and prefix-check operations on strings.
- A grid or board is searched for many target words simultaneously, where the words share prefixes that would otherwise be re-scanned from scratch for each one.

## The invariant
Every path from the root spells a prefix of at least one word that was inserted, and a node is marked "end of word" exactly when some inserted word ends there.

## The shape
1. Build a root node representing the empty prefix.
2. To insert a word: starting at the root, walk it character by character; at each character, follow the existing child for that character if one exists, or create a new one if it doesn't.
3. After consuming the whole word, mark the final node reached as "end of word" — this is what distinguishes a word that was actually inserted from a string that merely happens to be a prefix of a longer inserted word.
4. To check whether a word exists: walk the same way, character by character; if any character has no matching child, the word is absent; if you consume the whole word, it exists only if the final node is marked "end of word."
5. To check whether a prefix exists: walk the same way, but stop the check at consuming all prefix characters — no "end of word" marker is required, reaching the node at all is enough.
6. For wildcard search, at a wildcard character branch into every child of the current node instead of following one specific character, and continue the search from each.
7. For search-many-words-on-a-grid problems, insert all target words into one trie first, then do a single traversal of the grid, walking the trie alongside the grid path — abandoning a grid path as soon as it no longer matches any trie path, which prunes work shared prefixes would otherwise repeat.

## The named algorithms

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Trie (prefix tree) construction and traversal | Insert, exact-word lookup, and prefix lookup over a dictionary of strings | Store shared prefixes exactly once, as a shared path from the root, instead of storing every full string separately | Insert/search: O(L) time per word, L = word length; O(total characters across all inserted words) space |

There is really one named structure here, but its two operating modes matter: exact word search (must land on an "end of word" node) and prefix search (any node reached counts). The grid-search combination — inserting a whole dictionary into a trie, then walking the grid alongside it — is the classic technique that turns an otherwise repeated-work brute force into a single pass, and it's worth naming as a technique even though it isn't a separately-named algorithm.

## Worked micro-example
Insert the words: "cat", "car", "dog".

- Insert "cat": root → c (new) → a (new) → t (new, marked end-of-word).
- Insert "car": root → c (exists, reuse) → a (exists, reuse) → r (new, marked end-of-word). Note "c" and "a" are shared with "cat" — only one new node (`r`) was created.
- Insert "dog": root → d (new) → o (new) → g (new, marked end-of-word).

Resulting trie (end-of-word nodes marked with *):
```
root
├── c
│   └── a
│       ├── t*
│       └── r*
└── d
    └── o
        └── g*
```

**Search "ca":** walk root → c → a. Both exist. Reached node `a`, but it is not marked end-of-word (no word "ca" was inserted). Search returns false.

**StartsWith "ca":** walk root → c → a. Both exist, and reaching the node is all that's required. Returns true.

**Search "car":** walk root → c → a → r. All exist, and `r` is marked end-of-word. Returns true.

## Complexity
Insert and exact-word search both cost O(L) time, where L is the length of the word being inserted or searched — independent of how many other words are already in the trie, because each step follows exactly one child pointer per character. Space is O(total characters across all inserted words) in the worst case (no shared prefixes at all), but drops well below that when words share prefixes, since shared prefixes are stored once. Wildcard search costs more: a `.` can force branching into every child at that position, so worst-case time grows with the branching factor raised to the number of wildcards.

## Where it breaks
If the dictionary is queried only once, or the strings share almost no prefixes, the upfront cost of building a trie buys nothing over a plain hash set — a trie's advantage is amortized across many prefix-related queries against the same fixed set. It also does not help when the question is about substrings appearing anywhere within a word (not just at the start) — that calls for other string structures, not a trie keyed on prefixes.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Hash set / hash map of strings | A hash set answers "is this exact string present?" in O(1) but cannot answer "does any string start with this prefix?" without scanning everything; a trie answers both natively. |
| General trees (09-trees) | A trie is a tree, but its branching is keyed specifically by alphabet characters and its defining operation is prefix-walking, not the general parent/child recursion of arbitrary tree problems. |

## Common traps
- Forgetting the end-of-word marker entirely, so a search for a string that is merely a prefix of some inserted word (like searching "ca" when only "cat" was inserted) wrongly reports the word as present.
- Rebuilding the trie from scratch for every query instead of building it once and reusing it across all queries — this throws away the entire point of the preprocessing.
- Mismanaging the child lookup structure (e.g., a fixed-size 26-array assumed for lowercase letters, but the actual input includes digits, uppercase, or Unicode) causing out-of-bounds or missed matches.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Longest Common Prefix | Easy | 4 |
| Implement Trie (Prefix Tree) | Medium | 6 |
| Design Add and Search Words Data Structure | Medium | 2 |
| Word Search II | Hard | 2 |
| Top K Frequent Words | Medium | 1 |
| Design In-Memory File System | Hard | 1 |
| Palindrome Pairs | Hard | 1 |
