# LeetCode MCP — setup and troubleshooting

The two rules that matter (never relay `hints`; four tools are denied) are in `CLAUDE.md`. This is the setup detail and the diagnosis path.


Server `leetcode`, version-pinned in **`.mcp.json` at the project root**. Public tools only by default.

**If the leetcode tools are missing, do not tell the learner to restart.** A restart costs them tokens and fixes nothing when the cause is configuration. Check, in order: `.mcp.json` is at the project root (Claude Code reads nowhere else — there is no setting that redirects it); the project's MCP servers have been approved (`/mcp` shows this); and `npx -y @jinzcdev/leetcode-mcp-server@1.4.0 --site global` launches. A server absent from the session entirely — rather than failed or pending — means the config was never read.

| Tool | Use it for |
|---|---|
| `get_problem` | S0 — fetch statement, constraints, examples, difficulty, topic tags |
| `search_problems` | Finding siblings in a pattern, filtering by tag + difficulty |
| `get_daily_challenge` | `daily-drill` when they want today's LeetCode daily |

### What `get_problem` puts in your context — and what you may repeat

It returns `content`, `difficulty`, `topicTags`, `exampleTestcases`, `codeSnippets`, **`hints`** and **`similarQuestions`**.

| Field | Use |
|---|---|
| `content`, `exampleTestcases`, `difficulty`, `topicTags` | Free to use. This is the problem. |
| `similarQuestions` | **Useful** — real siblings for S1, better than guessing. |
| `codeSnippets` | Function signature only, no logic. Safe if they ask what to implement. |
| **`hints`** | **NEVER relay, quote, paraphrase or hint toward, at any stage before S5.** |

LeetCode's official hints are frequently the invariant or the data structure stated outright — rung 4 or 5 material, delivered for free. Repeating one at rung 1 skips four rungs and hands over the design decision. **You will have them in context the moment you call `get_problem` at S0. Having them is not permission to use them.** After S6 they are fine to discuss.

**Four tools are denied in `.claude/settings.json` and will fail if you call them:** `list_problem_solutions`, `get_problem_solution`, `submit_solution`, `run_code`.

Verified against the running server (v1.4.0, auth off, 9 tools exposed): `list_problem_solutions` and `get_problem_solution` **are** exposed and would return full community solutions. The deny list is what stops that. `submit_solution` and `run_code` are auth-gated and not exposed today; the deny keeps them blocked if auth is ever turned on.

Don't route around a denied tool by searching the web for the same content — that is the same violation with extra steps.

---

## Connector hygiene — the cheapest token saving available

Every MCP tool definition is injected into the system prompt **at session start**, whether or
not it is ever called. A session with many connectors enabled pays for all of them on every
single message.

Measured on a real session here: **175 MCP tools, 73.8k tokens — 37% of a 200k window, gone
before the first word.** Slack alone was 27 tools with long descriptions; nothing in lets-dsa
touches it.

**lets-dsa needs exactly two:**

| Connector | Why |
|---|---|
| `leetcode` | `get_problem` at S0, `search_problems` for siblings, `get_daily_challenge` |
| `visualize` | `visual-explainer`, the OA editor, the milestone card widget |

Everything else is overhead for a learning session. Turn the rest off in the composer's
**+ menu → Connectors**, or ask Claude to do it — the change applies to the session and
becomes the default for new ones, and nothing is uninstalled, so re-enabling takes one click
when you want Slack or a job board back.

**Not everything is a connector.** Plugins (`/plugin`) and built-in servers like
`scheduled-tasks` are managed in their own settings, not the Connectors menu.

### What you cannot do

**There is no lazy-loading.** Claude Code has no setting — project, user or `.mcp.json` — that
loads a tool index first and the full definition on demand. The harness decides what is in the
prompt, and a project cannot defer it. Choosing which servers are enabled is the entire lever.

### Why this matters more here than elsewhere

A teaching session is long: S0 through S6 with gates, hints and dry runs, on Sonnet or Haiku.
Context spent on tool definitions is context not spent on the learner's own words — their
invariant, their pseudocode, their defects — which is exactly what `Resume From:` exists to
rescue after a compaction. **Fewer connectors means fewer compactions means less re-asking.**
