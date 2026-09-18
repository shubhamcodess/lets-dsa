# Greedy

_Pattern id: 16-greedy · Depends on: 15-intervals · Problems available: 18_

## The one-sentence idea
At every step, take the choice that looks best right now, and trust — because you can prove it — that this never forecloses a better overall outcome.

## How to recognize it
- The question asks for a minimum number of steps, jumps, or operations, or a maximum profit/sum achieved by a sequence of choices.
- The scenario is phrased as jump games, gas stations, scheduling with deadlines, or "assign X to Y to satisfy as many as possible."
- You can imagine an exchange argument: if an optimal solution didn't make the locally-best choice at some step, you could swap it for the locally-best choice without making things worse.
- The decision at each step does not need to be revisited later — once made, it's final, and no combination of future decisions would make you regret it.

## The invariant
The partial solution built so far, using only locally-best choices, can always be extended into a solution that is at least as good as any other valid extension.

## The shape
1. Identify the single quantity to optimize at each step (soonest deadline, farthest reach, cheapest cost) — this defines "locally best."
2. Sort or order the input by that quantity if the input isn't already presented in the right order.
3. Walk through the input once, at each step taking the locally optimal action and updating a small amount of running state (a current reach, a running total, a count).
4. Before trusting this, mentally construct the exchange argument: take an arbitrary optimal solution, show that swapping in the greedy choice at the first point of disagreement cannot make it worse. If this argument fails to hold, the pattern does not apply here.
5. Return the accumulated result once the single pass completes.

## The named algorithms
This pattern is a technique, not a named algorithm family. There is no single greedy "algorithm" to recall — activity selection, interval scheduling, and jump-game reachability are all instances of the same idea (pick the locally best option and prove it's safe), but each problem needs its own exchange argument tailored to what "best" means there. Knowing the technique means knowing how to construct that argument, not memorizing a procedure.

## Worked micro-example
Take the jump-game-style array [2,3,1,1,4], where each value is the maximum jump length from that index, and the goal is to check if you can reach the last index.
Track `farthest reachable = 0`. At index 0 (value 2), farthest becomes max(0, 0+2) = 2.
At index 1 (value 3), since 1 <= farthest (2), it's reachable; farthest becomes max(2, 1+3) = 4.
At index 2 (value 1), since 2 <= farthest (4), reachable; farthest becomes max(4, 2+1) = 4.
At index 3 (value 1), reachable; farthest becomes max(4, 3+1) = 4.
At index 4 (the last index), since 4 <= farthest (4), it's reachable. The greedy choice — always tracking the single farthest point reached so far, never trying combinations of earlier jumps — is enough because a farther reach is never worse than a shorter one for any future move.

## Complexity
Typically O(n) or O(n log n) time — O(n) if the input can be scanned directly, O(n log n) if it must be sorted first (by deadline, by start time, by ratio). Space is usually O(1) beyond the sort, since greedy keeps only a small constant amount of running state rather than a table of subproblem answers.

## Where it breaks
Greedy breaks when choices interact — when taking the locally best option now can make a *later* choice strictly worse in a way that isn't recoverable, and no exchange argument can patch it. The signal that you need DP instead: you find yourself wanting to try multiple options at a step "just in case," or a counterexample surfaces where the greedy pick leads to a dead end while a different, locally worse pick would have succeeded. If you cannot complete the exchange-argument sentence — "swapping toward the greedy choice never hurts" — for your specific problem, it likely needs 17-1d-dp instead.

## Confusable with
| Also looks like | Tell them apart by |
|---|---|
| 17-1d-dp | If the greedy choice can be wrong depending on what happens later (you'd need to "undo" it), the problem needs a table of subproblem answers, not a single pass. |
| 15-intervals | Interval scheduling-to-maximize-count problems are a greedy technique applied to intervals; if the problem is only about merging/overlap with no selection trade-off, it's plain intervals, not greedy. |
| Backtracking/brute force | If you can't articulate why the local choice is safe, and the only way to be sure is to try all options, that's backtracking — greedy is what you get once you've found the safe shortcut. |

## Common traps
- Assuming a greedy strategy works without testing it against a small counterexample first — it is very easy to be convinced by one example that happens to work by luck.
- Applying greedy to a problem where choices actually interact, when the correct approach is DP — this produces code that passes a few test cases but fails on inputs where an earlier "obviously best" choice blocks a better later outcome.

## Problems in this pattern
| Problem | Difficulty | Sheets |
|---|---|---|
| Maximum Subarray | Medium | 7 |
| Jump Game | Medium | 4 |
| Assign Cookies | Easy | 3 |
| Maximum Number of Non-Overlapping Substrings | Hard | 3 |
| Gas Station | Medium | 2 |
| Hand of Straights | Medium | 2 |
| Jump Game II | Medium | 2 |
| Valid Parenthesis String | Medium | 2 |
