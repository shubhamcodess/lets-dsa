# Attribution and scope of the licence

The [MIT licence](LICENSE) covers **this framework** — the skills, subagents, scripts,
pattern briefs, the 20-pattern taxonomy, the foundations layer and the documentation.

It does not, and cannot, grant rights over the curated problem lists this project builds on.

## What this repository actually stores

`curriculum/merged.json` holds **factual metadata and links**, not anyone else's content:

| Stored | Not stored |
|---|---|
| LeetCode slug, problem id, title, difficulty | problem statements |
| topic tags from LeetCode's public API | editorials or explanations |
| which curated sheets contain a problem | any solution, in any language |
| links to free articles and videos | the contents of those articles |

Problem statements are fetched live from LeetCode when you work on a problem and are never
committed. Solutions are never stored at all — four MCP tools that could retrieve one are
denied at the project level.

## Sources

Ordering and selection draw on these publicly published lists. All credit for the curation
is theirs:

- [NeetCode 150](https://neetcode.io/) — Navdeep Singh
- [Striver's A2Z, SDE, Blind 75 and 79 sheets](https://takeuforward.org/) — Raj Vikramaditya (takeuforward)
- [CodingShuttle CS SDE Sheet](https://www.codingshuttle.com/)
- [RisingBrain](https://risingbrain.org/sheet) — pattern taxonomy, sub-pattern identification signals, and company tags
- [LeetCode](https://leetcode.com/) — problem data via its public GraphQL API and the
  [leetcode-mcp-server](https://github.com/jinzcdev/leetcode-mcp-server)

If you maintain one of these lists and would like the integration changed or removed, open
an issue and it will be actioned.

## A note on facts and compilations

Individual facts — that a problem exists, its difficulty, its slug — are generally not
copyrightable. The *selection and arrangement* of a curated list can attract database or
compilation rights in some jurisdictions, notably the EU.

This is not legal advice. If you fork this and redistribute it commercially, look into that
yourself. The framework is MIT; the judgement of which problems are worth solving belongs to
the people who did that work.
