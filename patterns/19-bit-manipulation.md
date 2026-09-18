# Bit Manipulation

_Pattern id: 19-bit-manipulation · Depends on: 01-arrays-hashing · Problems available: 14_

## The one-sentence idea
Treat an integer as a fixed-width array of independent bits, and use XOR to cancel, AND to mask, and shifts to move, instead of ordinary arithmetic.

## How to recognize it
- The problem explicitly asks for a solution without extra space, or without using arithmetic operators like +, -, *, /.
- It talks about counting set bits, finding a single number among duplicates or pairs, or flipping/toggling individual bits.
- Subsets of a small set are being represented or enumerated as a bitmask, where each bit stands for "is this element included."

## The invariant
Each bit position can be reasoned about completely independently of every other bit position — operations on one bit never depend on the value of any other bit.

## The shape
1. Identify what a single bit represents in the problem: membership in a subset, a binary digit of a number, or a flag/state that's either on or off.
2. Choose the operation that matches the needed transformation: XOR to toggle or to cancel out a value that appears an even number of times, AND with a mask to check or isolate specific bits, OR to set a bit, shifts to move a value into or out of a specific position.
3. If the problem involves enumerating all possibilities over a small set (subsets, states), loop an integer from 0 up to 2^n - 1 and treat each one as a bitmask, reading off which elements are "in" by checking each bit.
4. If the problem involves peeling off bits one at a time (counting them, or processing them individually), use a loop that repeatedly isolates the lowest set bit or shifts the number right, stopping when the number reaches zero.
5. Watch the boundaries: decide up front whether the problem is working within a fixed width (32-bit signed integers, with sign extension on right shifts) or with arbitrary-precision integers, since the two behave differently at the edges.

## The named algorithms
| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Brian Kernighan's algorithm | The number of set bits in an integer | Repeatedly clear the lowest set bit using `n AND (n-1)`, which flips exactly one bit off each time, and count how many iterations it takes to reach zero | O(k) time where k is the number of set bits, O(1) space |

Brian Kernighan's algorithm is faster than checking every one of the 32 (or 64) bit positions one by one, because it does exactly one iteration per set bit rather than one iteration per bit position — on a sparse number (few 1s), it finishes almost immediately. The trick, `n AND (n-1)`, works because subtracting 1 from n flips the lowest set bit off and every bit below it on, so ANDing with the original number keeps only the bits above that point, clearing the lowest 1 in a single step.

## Worked micro-example
Take n = 6, in binary 110. Find the number of set bits using Brian Kernighan's algorithm.
Step 1: n = 110 (6). n - 1 = 101 (5). n AND (n-1) = 110 AND 101 = 100 (4). One bit cleared; count = 1.
Step 2: n = 100 (4). n - 1 = 011 (3). n AND (n-1) = 100 AND 011 = 000 (0). Another bit cleared; count = 2.
Step 3: n = 0. Loop stops, since there are no more set bits to clear.
Result: 6 has 2 set bits, matching 110 having two 1s. Each step removed exactly one 1, in two steps rather than checking all three bit positions individually.

## Complexity
Most bit-manipulation problems run in O(1) or O(log(max value)) time, since the number of bits in a fixed-width integer is a small constant (32 or 64), and even "loop over each bit" solutions are bounded by that constant. Space is O(1), since bits are manipulated directly on the integer itself with no auxiliary structure, aside from bitmask-subset problems which may need O(2^n) space or time to enumerate every mask.

## Where it breaks
It breaks when the problem's structure isn't actually about individual bits at all — if the numbers involved are just being used as ordinary quantities (sums, comparisons, ranges) with no bitwise operation making the solution shorter or the space usage smaller, reaching for bit tricks adds complexity without benefit. It's also a poor fit when the language uses arbitrary-precision integers and the problem doesn't specify a bit width, since operations like "invert all bits" become ambiguous without a fixed number of bits to invert.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| Hashing (01-arrays-hashing) | "Find the single number among duplicates" can be done with a hash set, but the bit-manipulation version uses XOR to do it in O(1) space instead of O(n) — the signal is the extra-space constraint. |
| 20-math-geometry | Both can involve numeric manipulation (like Pow(x,n) using repeated squaring, which resembles shifting), but math-geometry problems reason about numeric value and mathematical properties, while bit manipulation reasons about individual binary digits. |
| Subset enumeration via backtracking | Enumerating all subsets can be done recursively (backtracking) or by looping over bitmasks 0 to 2^n - 1; the bitmask version is preferred when subsets need to be compared, combined, or looked up quickly, since integers are easy to hash and compare. |

## Common traps
- Sign extension on right shift for negative numbers: an arithmetic right shift fills new bits with copies of the sign bit, which can produce surprising results if you expected zeros to fill in.
- Assuming a fixed 32-bit width in a language with arbitrary-precision integers (like Python), which can make bit-inversion or overflow-dependent tricks behave differently than in a fixed-width language like Java or C++.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Counting Bits | Easy | 3 |
| Number of 1 Bits | Easy | 3 |
| Reverse Bits | Easy | 3 |
| Single Number | Easy | 3 |
| Maximum XOR With an Element From Array | Hard | 4 |
| Maximum XOR of Two Numbers in an Array | Medium | 3 |
| Reverse Integer | Medium | 3 |
| Missing Number | Easy | 2 |
