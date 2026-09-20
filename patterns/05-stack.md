# Stack

_Pattern id: 05-stack · Depends on: 01-arrays-hashing · Problems available: 13_

## The one-sentence idea
Last-in-first-out storage matches any structure where the most recently opened, unresolved thing must be the first one resolved.

## How to recognize it
- The problem involves nesting, brackets, or matched pairs (parentheses, tags, quotes).
- It involves undo, backtracking, or "the most recent X" (the last operation performed, the innermost unresolved item).
- The task is to parse or evaluate an expression, especially one with nested sub-expressions.
- You notice the natural solution would be recursive, but the problem wants (or the constraints demand) an iterative version — recursion's call stack is itself a stack, and simulating it explicitly is the tell.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **Parenthesis & Scoring** | Problem mentions parentheses, balanced brackets, scoring, or generation | Push opening symbols and validate closing ones; sometimes track count or score |
| **Recursive Stack** | Problem mentions reverse/insert/delete recursively, sort stack, merge lists, or check palindrome recursively | Handle top/head element recursively → recurse on remaining stack/list → combine/insert results |
| **Stack Simulation / Undo Operation** | Problem mentions “undo,” “remove duplicates,” or “backspace string” operations | Simulate operations using a stack → pop on undo, remove adjacent duplicates, collapse characters |
| **Stack-Based Design** | Problem mentions designing stack/queue systems or custom operations | Use two stacks to implement another data structure or maintain extra info |

## The invariant
The stack holds exactly the items that have been opened but not yet closed, with the innermost (most recently opened) one on top.

## The shape
1. Walk through the input from left to right, one element or token at a time.
2. When encountering something that "opens" a scope (an opening bracket, the start of an operation, a value to defer), push it onto the stack.
3. When encountering something that "closes" a scope (a closing bracket, an operator that resolves pending values), look at the top of the stack rather than searching the whole structure — it holds exactly the thing this closer must match or combine with.
4. Pop and resolve that top item, checking that it's compatible with what's being closed; if it isn't, that's an immediate contradiction (e.g., mismatched brackets).
5. Continue until the input is exhausted.
6. At the end, the stack should be empty if everything was properly opened and closed; anything left on the stack represents an unresolved item.

## The named algorithms
This pattern is a technique, not a named algorithm family. There is no canonical stack algorithm beyond the data structure's own last-in-first-out discipline — the skill is recognizing which problems have that "most recent unresolved thing" shape.

| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|

## Worked micro-example
Input: string `"({[]})"`. Task: determine whether the brackets are balanced.
Start with an empty stack.
- `(`: an opener. Push it. Stack: [ ( ].
- `{`: an opener. Push it. Stack: [ (, { ].
- `[`: an opener. Push it. Stack: [ (, {, [ ].
- `]`: a closer. Top of stack is `[`, which matches. Pop it. Stack: [ (, { ].
- `}`: a closer. Top of stack is `{`, which matches. Pop it. Stack: [ ( ].
- `)`: a closer. Top of stack is `(`, which matches. Pop it. Stack: [ ] (empty).
End of input, and the stack is empty, so the brackets are balanced. If any closer had found a mismatched or missing opener on top, the string would have been immediately declared unbalanced.

## Complexity
Typical time is O(n), driven by a single pass through the input where each element is pushed and popped at most once. Typical space is O(n) in the worst case, driven by how many items can be simultaneously "open" (for deeply nested input, the stack can grow to the size of the input).

## Where it breaks
- The matching isn't strictly last-in-first-out — for example, if any open item could be closed by any later closer regardless of nesting order, a stack's ordering guarantee is irrelevant.
- The problem requires looking arbitrarily far back, not just at the most recent unresolved item (a stack only exposes its top).
- The structure has no natural notion of "opening" and "closing" at all, so there's nothing for a stack to track.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Monotonic Stack | A plain stack matches and resolves pairs as they close; a monotonic stack proactively discards elements that can never matter later, and stays sorted while doing it. |
| Linked List | Both can simulate sequential structure, but a stack only ever accesses its top, while a linked list problem typically needs arbitrary pointer rewiring. |
| Arrays & Hashing | Counting opens vs. closes with a running counter can look similar, but a counter alone can't verify *type* or *order* — only a stack (or explicit nesting check) can catch `([)]` as invalid despite balanced counts. |

## Common traps
- Popping from an empty stack when a closer appears with nothing open to match it, which must be treated as an immediate failure, not ignored.
- Checking balance only by counting openers and closers, which misses type mismatches and wrong ordering (equal counts don't guarantee valid nesting).
- Forgetting to check that the stack is empty at the very end — leftover unclosed openers are also a failure, not just a mismatch mid-scan.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Valid Parentheses | Easy | 6 |
| Implement Queue using Stacks | Easy | 4 |
| Implement Stack using Queues | Easy | 3 |
| Min Stack | Medium | 5 |
| Asteroid Collision | Medium | 3 |
| Evaluate Reverse Polish Notation | Medium | 2 |
| Basic Calculator II | Medium | 1 |
| Basic Calculator | Hard | 1 |
