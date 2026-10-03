/**
 * build-data — turns the lets-dsa markdown + json into the static JSON the site reads.
 *
 * Mechanical by design: frontmatter via gray-matter, body via remark (mdast), split on
 * `## ` headings, each heading mapped to a field by config/content.config.json. Markdown
 * and code highlighting are rendered here, once, so the browser ships no parser.
 *
 *   DSA_ROOT   where the data lives (default: the folder above site/)
 *   SITE_MODE  "private" (default) | "public" — public strips sections marked private
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkRehype from 'remark-rehype';
import rehypeRaw from 'rehype-raw';
import rehypeStringify from 'rehype-stringify';
import rehypeShiki from '@shikijs/rehype';
import { toString } from 'mdast-util-to-string';

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ROOT = path.resolve(process.env.DSA_ROOT ?? path.join(SITE, '..'));
const MODE = process.env.SITE_MODE === 'public' ? 'public' : 'private';
const OUT = path.join(SITE, 'public', 'data');

const content = readJson(path.join(SITE, 'config/content.config.json'));
const site = readJson(path.join(SITE, 'config/site.config.json'));
const src = (k: string) => path.join(ROOT, site.source[k]);
const warnings: string[] = [];

type Node = any;
type Rule = { key: string; match: string; label: string; kind?: string; recall?: string | number; private?: boolean; skip?: boolean };

// ---------------------------------------------------------------- helpers

function readJson(p: string, fallback: any = undefined) {
  if (!fs.existsSync(p)) {
    if (fallback !== undefined) return fallback;
    throw new Error(`missing ${p}`);
  }
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function write(rel: string, data: unknown) {
  const p = path.join(OUT, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(data));
}

function walkMd(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) return walkMd(p);
    return e.name.endsWith('.md') ? [p] : [];
  });
}

const parser = unified().use(remarkParse).use(remarkGfm);
const renderer = unified()
  .use(remarkRehype, { allowDangerousHtml: true })
  .use(rehypeRaw)
  .use(rehypeShiki, {
    themes: { light: 'vitesse-light', dark: 'vitesse-dark' },
    defaultColor: false,
    fallbackLanguage: 'text',
  })
  .use(rehypeStringify);

async function render(nodes: Node[]): Promise<string> {
  const tree = await renderer.run({ type: 'root', children: structuredClone(nodes) } as Node);
  return String(renderer.stringify(tree as Node));
}

const text = (nodes: Node[]) => nodes.map((n) => toString(n)).join('\n\n').trim();

/** Soft line breaks become real ones — pseudocode is written line by line without list syntax. */
function hardBreaks(node: Node): Node {
  if (node.type === 'paragraph') {
    node.children = node.children.flatMap((c: Node) =>
      c.type === 'text' && c.value.includes('\n')
        ? c.value.split('\n').flatMap((v: string, i: number) => (i ? [{ type: 'break' }, { type: 'text', value: v }] : [{ type: 'text', value: v }]))
        : [c],
    );
  }
  node.children?.forEach(hardBreaks);
  return node;
}

/** Bare LeetCode URLs in the statement duplicate the header link — drop them, wherever they sit. */
function stripLeetcodeLinks(nodes: Node[]): Node[] {
  const bare = (n: Node) => n.type === 'link' && /^https?:\/\/leetcode\.com\/problems\//.test(n.url) && toString(n) === n.url;
  return nodes
    .map((n) => {
      if (n.type !== 'paragraph' || !n.children.some(bare)) return n;
      const children = n.children.filter((c: Node) => !bare(c));
      const last = children[children.length - 1];
      if (last?.type === 'text') last.value = last.value.replace(/\s+$/, '');
      return { ...n, children };
    })
    .filter((n) => !(n.type === 'paragraph' && !toString(n).trim()));
}

function tableOf(nodes: Node[]) {
  const t = nodes.find((n) => n.type === 'table');
  if (!t) return null;
  const [head, ...rows] = t.children.map((r: Node) => r.children.map((c: Node) => toString(c).trim()));
  return { head, rows };
}

/** Split a document on `## ` headings. Returns the h1 and the ordered sections. */
function sections(tree: Node) {
  let h1 = '';
  const out: { heading: string; nodes: Node[] }[] = [];
  let lead: Node[] = [];
  for (const n of tree.children) {
    if (n.type === 'html' && /^<!--/.test(n.value.trim())) continue;
    if (n.type === 'heading' && n.depth === 1) { h1 = toString(n); continue; }
    if (n.type === 'heading' && n.depth === 2) { out.push({ heading: toString(n).trim(), nodes: [] }); continue; }
    (out.length ? out[out.length - 1].nodes : lead).push(n);
  }
  return { h1, lead, sections: out };
}

function matchRule(heading: string, rules: Rule[]) {
  return rules.find((r) => new RegExp(r.match, 'i').test(heading));
}

const DATE = /\b(20\d\d-\d\d-\d\d)\b/g;
const iso = (v: unknown) => (v instanceof Date ? v.toISOString().slice(0, 10) : v ? String(v) : null);

// ---------------------------------------------------------------- sources

const patternsCfg = readJson(src('patternsConfig'), { patterns: [] }).patterns as any[];
const patternName = Object.fromEntries(patternsCfg.map((p) => [p.id, p.name]));
const stats = readJson(src('stats'), null);
const curriculum = readJson(src('curriculum'), { problems: {} }).problems as Record<string, any>;
const foundations = readJson(src('foundationsConfig'), { topics: [] }).topics as any[];

// ---------------------------------------------------------------- questions

async function parseQuestion(file: string) {
  const raw = fs.readFileSync(file, 'utf8');
  const { data: fm, content: body } = matter(raw);
  const { h1, sections: secs } = sections(parser.parse(body));
  const slug = fm.problem ?? path.basename(file, '.md');
  const cur = curriculum[slug] ?? {};

  const out: Record<string, any> = {};
  const other: any[] = [];
  const plain: Record<string, string> = {};
  const activity = new Set<string>();

  for (const s of secs) {
    const rule = matchRule(s.heading, content.sections) as Rule | undefined;
    if (!rule) {
      warnings.push(`${path.relative(ROOT, file)}: unmapped heading "## ${s.heading}" → other`);
      other.push({ heading: s.heading, html: await render(s.nodes) });
      continue;
    }
    if (MODE === 'public' && rule.private) continue;
    let nodes = s.nodes;
    // The LeetCode link is rendered in the header; drop a paragraph that is only that link.
    if (rule.key === 'problem') nodes = stripLeetcodeLinks(nodes);
    if (rule.kind === 'pre') nodes = nodes.map((n) => hardBreaks(structuredClone(n)));
    const note = s.heading.match(/\(([^)]+)\)\s*$/)?.[1] ?? null;
    const langs = nodes.filter((n) => n.type === 'code').map((n) => n.lang).filter(Boolean);
    const entry = {
      heading: s.heading,
      note,
      kind: rule.kind,
      html: await render(nodes),
      table: rule.kind === 'table' ? tableOf(nodes) : undefined,
      langs: langs.length ? langs : undefined,
      hasCode: langs.length > 0 || nodes.some((n) => n.type === 'code'),
    };
    if (out[rule.key]) out[rule.key].html += entry.html; // repeated heading: append
    else out[rule.key] = entry;
    plain[rule.key] = text(nodes);
    if (rule.key === 'sessionLog' || rule.key === 'revisitLog') for (const m of text(nodes).matchAll(DATE)) activity.add(m[1]);
  }

  const solvedOn = iso(fm.solved_on);
  const firstTouched = iso(fm.first_touched);
  if (solvedOn) activity.add(solvedOn);
  if (firstTouched) activity.add(firstTouched);

  // Defect classes for the error profile: any column named Class.
  const defects: string[] = [];
  const dt = out.defects?.table;
  if (dt) {
    const ci = dt.head.findIndex((h: string) => /class/i.test(h));
    if (ci >= 0) for (const r of dt.rows) if (r[ci] && /^[A-Z][A-Z-]+$/.test(r[ci])) defects.push(r[ci]);
  }

  const fmOut: Record<string, any> = { ...fm };
  if (MODE === 'public') for (const k of content.publicStripFrontmatter) delete fmOut[k];
  for (const k of Object.keys(fmOut)) if (fmOut[k] instanceof Date) fmOut[k] = iso(fmOut[k]);

  const verified = MODE === 'public' ? null : fm.accepted_verified ?? null;
  const summary = {
    slug,
    id: fm.leetcode_id ?? cur.leetcode_id ?? null,
    title: fm.title ?? h1.replace(/\s*\(#\d+\)\s*$/, ''),
    difficulty: fm.difficulty ?? cur.difficulty ?? null,
    pattern: fm.pattern ?? cur.pattern ?? path.basename(path.dirname(file)),
    patternName: patternName[fm.pattern] ?? fm.pattern,
    technique: cur.subpattern ?? null,
    status: fm.status ?? 'in_progress',
    stage: fm.stage_reached ?? null,
    mode: fm.mode ?? null,
    path: fm.path ?? null,
    solvedOn,
    firstTouched,
    hints: Number(fm.hints_used ?? 0),
    attempts: Number(fm.attempts ?? 0),
    explanation: MODE === 'public' ? null : fm.explanation ?? null,
    wrongGuesses: MODE === 'public' ? [] : fm.s1_wrong_guesses ?? [],
    verifiedUrl: typeof verified === 'string' && verified.startsWith('http') ? verified : null,
    verified: verified ? (String(verified).startsWith('http') ? 'submission' : String(verified)) : null,
    srs: { due: iso(fm.srs_due ?? fm.revisit_on), grade: fm.srs_grade ?? null, reps: fm.srs_reps ?? 0, lapses: fm.srs_lapses ?? 0 },
    tags: cur.topic_tags ?? [],
    companies: MODE === 'public' ? [] : cur.companies ?? [],
    lists: cur.lists ?? [],
    minutes: cur.avg_time_mins ?? null,
    link: `https://leetcode.com/problems/${slug}/`,
    excerpt: (plain.signal || plain.intuition || '').replace(/\s+/g, ' ').slice(0, 220),
    sheet: {
      signal: (plain.signal ?? '').replace(/\s+/g, ' ').trim(),
      intuition: firstSentences(plain.intuition ?? '', 2),
      complexity: optimalRow(out.complexity?.table ?? out.ladder?.table),
    },
    langs: [...new Set([...(out.solution?.langs ?? []), ...(out.canonical?.langs ?? [])])],
    defects,
    activity: [...activity].sort(),
  };

  const detail = {
    ...summary,
    frontmatter: fmOut,
    resources: cur.resources ?? null,
    sections: out,
    other,
  };
  const search = { slug, signal: plain.signal ?? '', intuition: plain.intuition ?? '', notes: plain.notes ?? '' };
  return { summary, detail, search };
}

function firstSentences(s: string, n: number) {
  const flat = s.replace(/\s+/g, ' ').trim();
  const parts = flat.match(/[^.!?]+[.!?]+(\s|$)/g);
  return (parts ? parts.slice(0, n).join('') : flat).trim();
}

/** Pull the optimal row's time/space from a ladder or complexity table, whichever exists. */
function optimalRow(t: { head: string[]; rows: string[][] } | null) {
  if (!t) return null;
  const ti = t.head.findIndex((h) => /time/i.test(h));
  const si = t.head.findIndex((h) => /space/i.test(h));
  if (ti < 0) return null;
  const row = t.rows.find((r) => /optimal|mine|yours/i.test(r[0])) ?? t.rows[t.rows.length - 1];
  return { time: row[ti] ?? '', space: si >= 0 ? row[si] ?? '' : '' };
}

// ---------------------------------------------------------------- patterns

function tiers() {
  const depth: Record<string, number> = {};
  const byId = Object.fromEntries(patternsCfg.map((p) => [p.id, p]));
  const d = (id: string): number => (depth[id] ??= 1 + Math.max(0, ...((byId[id]?.depends_on ?? []) as string[]).map(d)));
  patternsCfg.forEach((p) => d(p.id));
  return depth;
}

async function buildPatterns(solved: any[]) {
  const tier = tiers();
  const statRow = Object.fromEntries((stats?.patterns ?? []).map((p: any) => [p.pattern, p]));
  const list = [];
  for (const p of patternsCfg) {
    const mine = solved.filter((q) => q.pattern === p.id);
    const done = mine.filter((q) => q.status === 'solved');
    const s = statRow[p.id];
    const available = s?.available ?? Object.values(curriculum).filter((c: any) => c.pattern === p.id).length;
    const band = s?.band ?? (done.length ? 'exposed' : 'untouched');
    const avgHints = done.length ? +(done.reduce((a, q) => a + q.hints, 0) / done.length).toFixed(1) : null;
    const summary = {
      id: p.id,
      name: p.name,
      tier: tier[p.id],
      dependsOn: p.depends_on ?? [],
      coreIdea: p.core_idea ?? '',
      signals: p.signals ?? [],
      invariant: p.invariant_shape ?? '',
      traps: p.common_traps ?? [],
      available,
      solved: done.length,
      inProgress: mine.length - done.length,
      band,
      avgHints,
      problems: mine.map((q) => q.slug),
    };
    list.push(summary);

    const briefFile = path.join(src('patternBriefs'), `${p.id}.md`);
    const brief: Record<string, any> = {};
    if (fs.existsSync(briefFile)) {
      const { sections: secs } = sections(parser.parse(fs.readFileSync(briefFile, 'utf8')));
      for (const s of secs) {
        const rule = matchRule(s.heading, content.patternSections) as Rule | undefined;
        if (!rule) { warnings.push(`patterns/${p.id}.md: unmapped heading "## ${s.heading}"`); continue; }
        if (rule.skip) continue;
        brief[rule.key] = { label: rule.label, html: await render(s.nodes) };
      }
    }
    write(`patterns/${p.id}.json`, { ...summary, brief });
  }
  return list;
}

// ---------------------------------------------------------------- foundations

async function buildFoundations() {
  const out = [];
  for (const f of foundations) {
    const file = path.join(src('topics'), `${f.id}.md`);
    let fm: any = {};
    let secs: any[] = [];
    if (fs.existsSync(file)) {
      const parsed = matter(fs.readFileSync(file, 'utf8'));
      fm = parsed.data;
      for (const s of sections(parser.parse(parsed.content)).sections) secs.push({ heading: s.heading, html: await render(s.nodes) });
    }
    out.push({
      id: f.id,
      name: f.name,
      why: f.why_first,
      minutes: f.est_minutes,
      gates: f.gates_patterns ?? [],
      exercises: f.exercise_count ?? 0,
      resources: (f.resources ?? []).filter((r: any) => r.article || r.youtube),
      status: fm.status ?? 'not_started',
      learnedOn: iso(fm.learned_on),
      override: !!fm.foundation_override,
      sections: MODE === 'public' ? [] : secs,
    });
  }
  return out;
}

// ---------------------------------------------------------------- main

async function main() {
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(OUT, { recursive: true });

  const files = walkMd(src('questions'));
  const parsed = [];
  for (const f of files) {
    try { parsed.push(await parseQuestion(f)); }
    catch (e) { warnings.push(`${path.relative(ROOT, f)}: failed to parse — ${(e as Error).message}`); }
  }
  parsed.sort((a, b) => (b.summary.solvedOn ?? b.summary.firstTouched ?? '').localeCompare(a.summary.solvedOn ?? a.summary.firstTouched ?? ''));
  for (const p of parsed) write(`problems/${p.summary.slug}.json`, p.detail);

  const problems = parsed.map((p) => p.summary);
  const patterns = await buildPatterns(problems);
  const topics = await buildFoundations();

  const activity: Record<string, number> = {};
  for (const p of problems) for (const d of p.activity) activity[d] = (activity[d] ?? 0) + 1;

  const defectCounts: Record<string, string[]> = {};
  for (const p of problems) for (const d of p.defects) (defectCounts[d] ??= []).push(p.slug);
  const confusions: Record<string, number> = {};
  for (const p of problems) for (const g of p.wrongGuesses) if (patternName[g]) confusions[`${g}→${p.pattern}`] = (confusions[`${g}→${p.pattern}`] ?? 0) + 1;

  const solved = problems.filter((p) => p.status === 'solved');
  const byDifficulty = { Easy: 0, Medium: 0, Hard: 0 } as Record<string, number>;
  for (const p of solved) if (p.difficulty) byDifficulty[p.difficulty] = (byDifficulty[p.difficulty] ?? 0) + 1;

  write('index.json', {
    built: new Date().toISOString(),
    mode: MODE,
    available: Object.keys(curriculum).length || stats?.totals?.available || null,
    problems,
    patterns,
    activity,
    byDifficulty,
    bands: stats?.bands ?? null,
    errorProfile: MODE === 'public' ? null : {
      defects: Object.entries(defectCounts).map(([cls, slugs]) => ({ cls, count: slugs.length, slugs })).sort((a, b) => b.count - a.count),
      confusions: Object.entries(confusions).map(([k, times]) => { const [from, to] = k.split('→'); return { from, fromName: patternName[from] ?? from, to, toName: patternName[to] ?? to, times }; }).sort((a, b) => b.times - a.times),
    },
  });
  write('search.json', parsed.map((p) => p.search));
  write('foundations.json', topics);

  const rel = path.relative(process.cwd(), OUT) || '.';
  console.log(`build-data [${MODE}] ${problems.length} problems (${solved.length} solved) · ${patterns.length} patterns · ${topics.length} foundations → ${rel}`);
  if (warnings.length) {
    console.log(`\n${warnings.length} warning(s) — map these in config/content.config.json:`);
    for (const w of warnings) console.log(`  · ${w}`);
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
