import { useMemo, useState } from 'preact/hooks';
import type { Index, Summary } from '../lib/types';
import { isDue } from '../lib/dates';
import { Kicker } from '../components/atoms';
import { ProblemRows } from './Overview';

const SORTS: Record<string, [string, (a: Summary, b: Summary) => number]> = {
  recent: ['Most recent', (a, b) => (b.solvedOn ?? b.firstTouched ?? '').localeCompare(a.solvedOn ?? a.firstTouched ?? '')],
  number: ['Problem number', (a, b) => (a.id ?? 1e9) - (b.id ?? 1e9)],
  hints: ['Most hints', (a, b) => b.hints - a.hints || b.attempts - a.attempts],
  due: ['Due soonest', (a, b) => (a.srs.due ?? '9').localeCompare(b.srs.due ?? '9')],
  difficulty: ['Difficulty', (a, b) => rank(b.difficulty) - rank(a.difficulty)],
};
const rank = (d: string | null) => ({ Easy: 1, Medium: 2, Hard: 3 })[d ?? ''] ?? 0;

/** Filter state lives in the URL query so a filtered view can be bookmarked. */
function useQueryState() {
  const read = () => Object.fromEntries(new URLSearchParams(location.hash.split('?')[1] ?? ''));
  const [q, setQ] = useState<Record<string, string>>(read);
  const set = (k: string, v: string) => {
    const next = { ...q, [k]: v };
    if (!v) delete next[k];
    setQ(next);
    const qs = new URLSearchParams(next).toString();
    history.replaceState(null, '', `#/problems${qs ? `?${qs}` : ''}`);
  };
  return [q, set] as const;
}

export function Problems({ index }: { index: Index }) {
  const [q, set] = useQueryState();
  const text = (q.q ?? '').toLowerCase();

  const list = useMemo(() => {
    const out = index.problems.filter((p) => {
      if (q.pattern && p.pattern !== q.pattern) return false;
      if (q.d && p.difficulty !== q.d) return false;
      if (q.status === 'solved' && p.status !== 'solved') return false;
      if (q.status === 'progress' && p.status === 'solved') return false;
      if (q.status === 'due' && !isDue(p.srs.due)) return false;
      if (q.status === 'clean' && p.hints > 0) return false;
      if (text && !`${p.title} ${p.id} ${p.patternName} ${p.technique ?? ''} ${p.tags.join(' ')} ${p.excerpt}`.toLowerCase().includes(text)) return false;
      return true;
    });
    return out.sort(SORTS[q.sort ?? 'recent']?.[1] ?? SORTS.recent[1]);
  }, [index, q]);

  const patterns = index.patterns.filter((p) => p.problems.length);

  return (
    <div class="problems">
      <header class="page-head">
        <Kicker>The index</Kicker>
        <h1>Problems</h1>
        <p class="lede">{index.problems.length} in the notebook. Press <kbd>/</kbd> to search inside notes and intuitions.</p>
      </header>

      <div class="toolbar">
        <input class="filter-text" placeholder="Filter by title, number, tag…" value={q.q ?? ''} onInput={(e) => set('q', (e.target as HTMLInputElement).value)} />
        <div class="seg" role="group" aria-label="Difficulty">
          {['', 'Easy', 'Medium', 'Hard'].map((d) => (
            <button class={(q.d ?? '') === d ? 'on' : ''} onClick={() => set('d', d)}>{d || 'All'}</button>
          ))}
        </div>
        <select value={q.pattern ?? ''} onChange={(e) => set('pattern', (e.target as HTMLSelectElement).value)} aria-label="Pattern">
          <option value="">Every pattern</option>
          {patterns.map((p) => <option value={p.id}>{p.name}</option>)}
        </select>
        <select value={q.status ?? ''} onChange={(e) => set('status', (e.target as HTMLSelectElement).value)} aria-label="Status">
          <option value="">Any status</option>
          <option value="solved">Solved</option>
          <option value="progress">In progress</option>
          <option value="due">Due for recall</option>
          <option value="clean">Solved without hints</option>
        </select>
        <select value={q.sort ?? 'recent'} onChange={(e) => set('sort', (e.target as HTMLSelectElement).value)} aria-label="Sort">
          {Object.entries(SORTS).map(([k, [label]]) => <option value={k}>{label}</option>)}
        </select>
      </div>

      <p class="count">{list.length} shown</p>
      <ProblemRows problems={list} />
    </div>
  );
}
