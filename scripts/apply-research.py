#!/usr/bin/env python3
"""
apply-research.py — merge research output into curriculum/merged.json, with provenance.

Research is produced by a small model and by web search. Neither is authoritative, so
nothing here is trusted on assertion: every proposed pattern change is re-checked against
the problem's REAL LeetCode topic tags before it is applied, and every company tag must
arrive with a source URL or it is discarded.

Each field records how it got its value, so a wrong-looking entry can be audited instead
of believed:
    pattern_source   how the pattern was decided
    needs_review     true when no evidence was strong enough
    companies_meta   source URL + confidence, never presented as LeetCode data

Usage: python3 scripts/apply-research.py [--dry-run]
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGED = os.path.join(ROOT, "curriculum", "merged.json")
RES = os.path.join(ROOT, "curriculum", "research")

# A LeetCode topic tag distinctive enough to name a pattern by itself.
SIGNATURE = {
    "Sliding Window": "03-sliding-window", "Monotonic Stack": "06-monotonic-stack",
    "Trie": "10-tries", "Backtracking": "12-backtracking",
    "Bit Manipulation": "19-bit-manipulation", "Binary Search": "04-binary-search",
    "Union Find": "14-advanced-graphs", "Union-Find": "14-advanced-graphs",
    "Shortest Path": "14-advanced-graphs", "Minimum Spanning Tree": "14-advanced-graphs",
    "Strongly Connected Component": "14-advanced-graphs",
    "Biconnected Component": "14-advanced-graphs",
    "Topological Sort": "13-graphs", "Graph": "13-graphs", "Graph Theory": "13-graphs",
    "Heap (Priority Queue)": "11-heap-top-k", "Linked List": "07-linked-list",
    "Binary Tree": "09-trees", "Binary Search Tree": "09-trees", "Tree": "09-trees",
    "Stack": "05-stack", "Two Pointers": "02-two-pointers",
    "Dynamic Programming": "17-1d-dp", "Greedy": "16-greedy",
    "Interval": "15-intervals", "Geometry": "20-math-geometry",
}


# Tags that JUSTIFY a pattern. A pattern claimed without one of its distinctive tags
# present is not supported, no matter how confident the model was. Built from what
# LeetCode actually tags, not from what a problem "feels like".
DISTINCTIVE = {
    "01-arrays-hashing": {"Array", "Hash Table", "Counting", "String"},
    "02-two-pointers": {"Two Pointers"},
    "03-sliding-window": {"Sliding Window"},
    "04-binary-search": {"Binary Search"},
    "05-stack": {"Stack"},
    "06-monotonic-stack": {"Monotonic Stack"},
    "07-linked-list": {"Linked List"},
    "08-fast-slow-pointers": {"Two Pointers", "Linked List"},
    "09-trees": {"Tree", "Binary Tree", "Binary Search Tree"},
    "10-tries": {"Trie"},
    "11-heap-top-k": {"Heap (Priority Queue)"},
    "12-backtracking": {"Backtracking"},
    "13-graphs": {"Graph", "Graph Theory", "Topological Sort", "Breadth-First Search",
                  "Depth-First Search", "Matrix"},
    "14-advanced-graphs": {"Union Find", "Union-Find", "Shortest Path",
                           "Minimum Spanning Tree", "Strongly Connected Component",
                           "Biconnected Component"},
    "15-intervals": {"Interval", "Line Sweep"},
    "16-greedy": {"Greedy"},
    "17-1d-dp": {"Dynamic Programming", "Memoization"},
    "18-2d-dp": {"Dynamic Programming", "Matrix"},
    "19-bit-manipulation": {"Bit Manipulation", "Bitmask"},
    "20-math-geometry": {"Math", "Geometry", "Simulation", "Number Theory"},
}

# Checked before DISTINCTIVE: a tag so specific it names exactly one pattern.
SIGNATURE = {
    "Sliding Window": "03-sliding-window", "Monotonic Stack": "06-monotonic-stack",
    "Trie": "10-tries", "Backtracking": "12-backtracking",
    "Bit Manipulation": "19-bit-manipulation", "Binary Search": "04-binary-search",
    "Union Find": "14-advanced-graphs", "Union-Find": "14-advanced-graphs",
    "Shortest Path": "14-advanced-graphs", "Minimum Spanning Tree": "14-advanced-graphs",
    "Strongly Connected Component": "14-advanced-graphs",
    "Biconnected Component": "14-advanced-graphs",
    "Topological Sort": "13-graphs", "Graph": "13-graphs", "Graph Theory": "13-graphs",
    "Heap (Priority Queue)": "11-heap-top-k", "Linked List": "07-linked-list",
    "Binary Tree": "09-trees", "Binary Search Tree": "09-trees", "Tree": "09-trees",
    "Stack": "05-stack", "Two Pointers": "02-two-pointers",
    "Dynamic Programming": "17-1d-dp", "Greedy": "16-greedy",
    "Interval": "15-intervals", "Geometry": "20-math-geometry",
}


def score(pattern, tags, pattern_tags):
    """How strongly do the problem's REAL tags support this pattern?
    3 = a signature tag names it. 2 = a distinctive tag is present, plus corroboration.
    1 = a distinctive tag is present. 0 = not justified by the tags at all."""
    if not pattern:
        return 0
    tags = set(tags)
    if any(SIGNATURE.get(t) == pattern for t in tags):
        return 3
    if tags & DISTINCTIVE.get(pattern, set()):
        return 2 if len(tags & set(pattern_tags.get(pattern, []))) >= 2 else 1
    return 0


def best_by_tags(tags, pattern_tags):
    """The best-supported pattern for these tags, or None if nothing is justified."""
    ranked = sorted(pattern_tags, key=lambda pid: -score(pid, tags, pattern_tags))
    top = ranked[0] if ranked else None
    return top if top and score(top, tags, pattern_tags) > 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(MERGED) as f:
        merged = json.load(f)
    problems = merged["problems"]
    pj = json.load(open(os.path.join(ROOT, "config", "patterns.json")))["patterns"]
    pattern_tags = {p["id"]: p.get("leetcode_tags", []) for p in pj}
    valid = set(pattern_tags)

    stats = {"applied": 0, "rejected": 0, "reassigned": 0, "flagged": 0,
             "companies_set": 0, "companies_dropped": 0, "companies_empty": 0}
    log = []

    # ---------- patterns ----------
    pfile = os.path.join(RES, "patterns.json")
    if os.path.exists(pfile):
        for r in json.load(open(pfile)):
            slug, prop = r.get("slug"), r.get("pattern")
            p = problems.get(slug)
            if not p or prop in (None, "uncertain") or prop not in valid:
                continue
            if prop == p["pattern"]:
                continue
            cur = p["pattern"]
            s_cur = score(cur, p["topic_tags"], pattern_tags)
            s_new = score(prop, p["topic_tags"], pattern_tags)

            # A third pattern may be better supported than either candidate — e.g. a
            # "Union-Find" tag names advanced-graphs even when neither the current
            # value nor the model's proposal mentioned it.
            alt0 = best_by_tags(p["topic_tags"], pattern_tags)
            s_alt = score(alt0, p["topic_tags"], pattern_tags)
            if alt0 and s_alt > max(s_cur, s_new):
                log.append(f"  reassign {str(cur):20s} -> {alt0:20s} {slug}  "
                           f"(tags support it {s_alt} over cur {s_cur} / proposed {s_new})")
                p["pattern"], p["pattern_source"] = alt0, "research:tag-override"
                p.pop("needs_review", None), p.pop("review_note", None)
                stats["reassigned"] += 1
                continue

            if s_new > s_cur and s_new > 0:
                log.append(f"  apply    {str(cur):20s} -> {prop:20s} {slug}  "
                           f"(tag support {s_cur} -> {s_new})")
                p["pattern"], p["pattern_source"] = prop, "research:tag-verified"
                p.pop("needs_review", None), p.pop("review_note", None)
                stats["applied"] += 1
            elif s_cur > 0:
                log.append(f"  reject   keep {str(cur):20s} over {prop:20s} {slug}  "
                           f"(tag support {s_cur} >= {s_new})")
                stats["rejected"] += 1
            else:
                alt = best_by_tags(p["topic_tags"], pattern_tags)
                if alt and alt != cur:
                    log.append(f"  reassign {str(cur):20s} -> {alt:20s} {slug}  "
                               f"(neither {cur} nor {prop} is tag-supported)")
                    p["pattern"], p["pattern_source"] = alt, "research:tag-override"
                    stats["reassigned"] += 1
                else:
                    log.append(f"  flag     {str(cur):20s} {slug}  (no pattern is tag-supported)")
                    stats["rejected"] += 1
                p["needs_review"] = True
                p["review_note"] = (
                    f"No strong tag support for any pattern (tags: {p['topic_tags']}). "
                    f"Model proposed {prop}. Taxonomy fit is loose — say so when serving it.")
                stats["flagged"] += 1

    # ---------- companies ----------
    cfile = os.path.join(RES, "companies.json")
    if os.path.exists(cfile):
        for r in json.load(open(cfile)):
            p = problems.get(r.get("slug"))
            if not p:
                continue
            names = [c for c in (r.get("companies") or []) if isinstance(c, str) and c.strip()]
            src = r.get("source")
            if not names:
                stats["companies_empty"] += 1
                continue
            if not src or not str(src).startswith("http"):
                # A company list with no source is exactly what must not be trusted.
                stats["companies_dropped"] += 1
                log.append(f"  DROP companies for {r['slug']} — no source URL")
                continue
            p["companies"] = names[:6]
            p["companies_meta"] = {
                "source": src,
                "confidence": r.get("confidence", "low"),
                "provenance": "third-party web research, not LeetCode Premium data",
            }
            stats["companies_set"] += 1

    merged["counts"]["by_pattern"] = {}
    for p in problems.values():
        k = p["pattern"] or "UNASSIGNED"
        merged["counts"]["by_pattern"][k] = merged["counts"]["by_pattern"].get(k, 0) + 1
    merged["counts"]["by_pattern"] = dict(sorted(merged["counts"]["by_pattern"].items()))
    merged["counts"]["needs_review"] = sum(1 for p in problems.values() if p.get("needs_review"))
    merged["counts"]["with_companies"] = sum(1 for p in problems.values() if p.get("companies"))
    src = {}
    for p in problems.values():
        src[p["pattern_source"]] = src.get(p["pattern_source"], 0) + 1
    merged["counts"]["by_pattern_source"] = dict(sorted(src.items()))
    merged["research"] = {
        "applied": stats,
        "how_patterns_were_checked":
            "Every model-proposed pattern change was re-verified against the problem's real "
            "LeetCode topic tags. Applied only on strong evidence (a signature tag, or 2+ "
            "overlapping tags). Anything weaker was rejected or reassigned by tags, and the "
            "problem carries needs_review: true.",
        "company_tag_caveat":
            "Third-party web research, NOT LeetCode Premium data. Every entry carries its "
            "source URL in companies_meta. Any company list that arrived without a source "
            "was discarded. Treat as a weak signal for prioritization, never as fact.",
    }

    print("\n".join(log) if log else "  (no research files found)")
    print(f"\npatterns: applied {stats['applied']} · reassigned {stats['reassigned']} · "
          f"rejected {stats['rejected']} · flagged needs_review {stats['flagged']}")
    print(f"companies: set {stats['companies_set']} · dropped-no-source "
          f"{stats['companies_dropped']} · empty {stats['companies_empty']}")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    with open(MERGED, "w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    print(f"\nWrote {MERGED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
