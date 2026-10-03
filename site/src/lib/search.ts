import MiniSearch from 'minisearch';
import { loadIndex, loadSearch } from './data';
import type { Summary } from './types';

export interface Hit { slug: string; score: number; summary: Summary }

let engine: Promise<{ ms: MiniSearch; bySlug: Map<string, Summary> }> | null = null;

/** Built on first use: the full-text payload is fetched only when someone searches. */
function build() {
  engine ??= Promise.all([loadIndex(), loadSearch()]).then(([index, text]) => {
    const extra = new Map(text.map((t) => [t.slug, t]));
    const ms = new MiniSearch({
      idField: 'slug',
      fields: ['title', 'id', 'patternName', 'technique', 'tags', 'signal', 'intuition', 'notes'],
      searchOptions: { boost: { title: 4, id: 4, patternName: 2, technique: 2 }, prefix: true, fuzzy: 0.2 },
    });
    ms.addAll(index.problems.map((p) => ({
      ...p,
      id: p.id != null ? String(p.id) : '',
      tags: p.tags.join(' '),
      ...extra.get(p.slug),
      slug: p.slug,
    })));
    return { ms, bySlug: new Map(index.problems.map((p) => [p.slug, p])) };
  });
  return engine;
}

export async function search(q: string): Promise<Hit[]> {
  const { ms, bySlug } = await build();
  return ms.search(q.trim()).slice(0, 30).map((r) => ({ slug: r.id, score: r.score, summary: bySlug.get(r.id)! }));
}

export const warm = () => { void build(); };
