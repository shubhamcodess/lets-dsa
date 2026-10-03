import type { Index } from '../lib/types';
import { href } from '../lib/router';
import { Diff, Empty, Kicker } from '../components/atoms';
import { short, today } from '../lib/dates';

/** One page, print-ready: per pattern, the invariant; per problem, signal · intuition · cost. */
export function Sheet({ index }: { index: Index }) {
  const groups = index.patterns
    .map((p) => ({ p, list: index.problems.filter((q) => q.pattern === p.id && q.status === 'solved') }))
    .filter((g) => g.list.length);
  return (
    <div class="sheet">
      <header class="page-head">
        <Kicker>The night before · {short(today())}</Kicker>
        <h1>Cheat sheet</h1>
        <p class="lede">Every solved problem in one line of signal and one of intuition. <button class="btn ghost print-hide" onClick={() => print()}>Print</button></p>
      </header>
      {!groups.length && <Empty>Nothing solved yet.</Empty>}
      {groups.map(({ p, list }) => (
        <section class="sheet-group">
          <h2><a href={href('patterns', p.id)}>{p.name}</a></h2>
          {p.invariant && <p class="sheet-inv">{p.invariant}</p>}
          <dl>
            {list.map((q) => (
              <div class="sheet-row">
                <dt>
                  <a href={href('p', q.slug)}>{q.title}</a>
                  <Diff d={q.difficulty} />
                  {q.sheet.complexity && <span class="cost mono">{q.sheet.complexity.time}{q.sheet.complexity.space && ` · ${q.sheet.complexity.space}`}</span>}
                </dt>
                <dd>
                  {q.sheet.signal && <p><b>Signal.</b> {q.sheet.signal}</p>}
                  {q.sheet.intuition && <p><b>Hold.</b> {q.sheet.intuition}</p>}
                </dd>
              </div>
            ))}
          </dl>
        </section>
      ))}
    </div>
  );
}
