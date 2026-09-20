# Math & Geometry

_Pattern id: 20-math-geometry · Depends on: 01-arrays-hashing · Problems available: 13_

## The one-sentence idea
Find the mathematical or geometric property that already describes the answer, and use it directly instead of simulating the process step by step.

## How to recognize it
- The problem involves matrix rotation, spiral traversal, or another operation defined by describing motion around a 2-D grid.
- The problem talks about digits, primality, greatest common divisor, or modular arithmetic.
- The constraints explicitly warn about overflow, or mention numbers large enough that intermediate results could exceed a standard integer range.

## Sub-patterns inside this family

Finer cuts of the same idea. The **recognize** column is what to look for in a
problem statement — that is the transferable part.

| Sub-pattern | Recognize it when | What you do |
|---|---|---|
| **Array — General / Math** | Problem is a direct simulation or formula — Pascal’s triangle rows, spiral order, leaders — with no reusable pattern behind it | Work out the traversal order or recurrence by hand first, then translate it into index arithmetic with explicit boundary checks |

## The invariant
A specific mathematical property (a formula, a positional relationship, a parity or divisibility fact) holds true at every step of the process, and it is exactly this property that makes the shortcut valid instead of needing to simulate the full process.

## The shape
1. Restate the problem's operation in precise mathematical or positional terms — for a rotation, what does position (i, j) map to; for a digit problem, what does processing a number one digit at a time (via mod and integer division) look like.
2. Look for a property that lets you skip steps: a formula that computes the k-th result directly, a way to transform the operation in place without extra storage, or a number-theoretic fact (primes only need checking up to their square root, GCD reduces two numbers without ever listing factors).
3. Handle the plane or grid geometry, if present, by working out layer-by-layer or corner-by-corner logic explicitly (e.g., a matrix rotation as a transpose followed by a reversal, or a spiral as four shrinking boundaries), since these are usually simulations guided by a clean invariant rather than a single closed-form formula.
4. Guard against overflow and precision: decide whether intermediate values could exceed the safe integer range, and apply modular arithmetic, wider types, or early-exit checks as the problem's constraints suggest.
5. Apply the property or simulate the reduced number of steps to produce the final answer, verifying it against the stated invariant rather than against a full brute-force trace.

## The named algorithms
| Algorithm | What it computes | Key idea | Cost |
|---|---|---|---|
| Sieve of Eratosthenes | All prime numbers up to some limit n | Starting from 2, mark every multiple of each found prime as composite, so each composite number gets crossed out by its smallest prime factor | O(n log log n) time, O(n) space |
| Euclid's algorithm (GCD) | The greatest common divisor of two integers | Repeatedly replace the larger number with its remainder when divided by the smaller, since any common divisor of the two original numbers is also a common divisor of the remainder pair | O(log(min(a,b))) time, O(1) space |

The Sieve of Eratosthenes is efficient because each composite number is visited a small, bounded number of times (once per prime factor), rather than being tested individually for primality from scratch. Euclid's algorithm works because gcd(a, b) = gcd(b, a mod b) — the remainder operation shrinks the numbers geometrically fast, similar to how binary search halves a range, which is why it converges in a logarithmic number of steps even for very large integers.

## Worked micro-example
Trace Euclid's algorithm on gcd(18, 12).
Step 1: a=18, b=12. 18 mod 12 = 6. Replace: a=12, b=6.
Step 2: a=12, b=6. 12 mod 6 = 0. Replace: a=6, b=0.
Step 3: b is 0, so the algorithm stops. The answer is a = 6.
Check: 6 divides both 18 (18 = 6×3) and 12 (12 = 6×2), and no larger number divides both, confirming 6 is indeed the greatest common divisor. Each step replaced the pair with a strictly smaller pair carrying the same GCD, which is the invariant that makes stopping at remainder 0 correct.

## Complexity
Highly variable by problem: digit and GCD-style problems typically run in O(log(value)) time since they shrink the number geometrically each step; sieve-style problems run in O(n log log n) for generating results up to n; grid/matrix simulations (rotation, spiral) run in O(rows × cols) time since every cell must be visited once. Space is usually O(1) beyond the output itself, since the core trick is almost always about avoiding extra storage, not adding it — except the sieve, which needs O(n) space for its marking array.

## Where it breaks
It breaks when there is no clean mathematical shortcut to find — some problems that look like "math" are really simulation problems with no formula available, and forcing a search for a nonexistent closed-form wastes time better spent just simulating carefully. It also breaks when the "obvious" formula silently assumes inputs that don't hold in general (for example, a rotation formula assuming a square matrix when the grid is rectangular), so the geometric relationship must be re-derived for the actual shape given.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| 19-bit-manipulation | Both can involve manipulating numeric representations, but bit manipulation reasons about individual binary digits and fixed-width operations, while math-geometry reasons about numeric value, divisibility, or spatial position. |
| Simulation (general) | If a problem has no discoverable shortcut and genuinely must be stepped through exactly as described, it's plain simulation; math-geometry as a pattern applies once a property is found that lets you skip or shortcut steps. |
| 17-1d-dp | A problem counting arrangements or outcomes might look mathematical (e.g., combinatorial counting), but if it requires building up from overlapping subproblems rather than applying a direct formula, it belongs in 1-D DP instead. |

## Common traps
- Integer overflow on intermediate products or sums, especially in problems computing large powers, factorials, or coordinate products, where the final answer fits but an intermediate step does not.
- Applying an in-place transformation (like a rotation) twice to the same cell by mistake — a careless loop structure can revisit and re-modify a cell that was already moved into its final position.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Roman to Integer | Easy | 4 |
| Palindrome Number | Easy | 3 |
| Rotate Image | Medium | 6 |
| Set Matrix Zeroes | Medium | 6 |
| Pow(x, n) | Medium | 5 |
| Spiral Matrix | Medium | 4 |
| Permutation Sequence | Hard | 2 |
