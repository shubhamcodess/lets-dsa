import type { Index } from '../lib/types';
import { loadPattern, useData } from '../lib/data';
import { ROMAN, site } from '../lib/config';
import { href } from '../lib/router';
import { BandMark, Empty, Html, Kicker, Loading, SectionHead } from '../components/atoms';
import { ProblemRows } from './Overview';

export function Patterns({ index }: { index: Index }) {
  const tiers = [...new Set(index.patterns.map((p) => p.tier))].sort();
  const name = Object.fromEntries(index.patterns.map((p) => [p.id, p.name]));
  return (
    <div class="patterns">
      <header class="page-head">
        <Kicker>The families</Kicker>
        <h1>Patterns</h1>
        <p class="lede">Ordered so nothing appears before what it depends on. Each brief is about the pattern, not about me.</p>
      </header>
      {tiers.map((t) => (
        <section class="tier">
          <h2 class="tier-h">Tier {ROMAN[t] ?? t}</h2>
          <div class="pcards">
            {index.patterns.filter((p) => p.tier === t).map((p) => (
              <a class={`pcard band-${p.band}`} href={href('patterns', p.id)}>
                <div class="pcard-top">
                  <span class="pcard-id mono">{p.id.slice(0, 2)}</span>
                  <BandMark band={p.band} />
                </div>
                <h3>{p.name}</h3>
                <p>{p.coreIdea}</p>
                <div class="pcard-foot">
                  <span>{p.solved} of {p.available} solved</span>
                  {p.dependsOn.length > 0 && <span class="dep">after {p.dependsOn.map((d) => name[d] ?? d).join(', ')}</span>}
                </div>
                <div class="pcard-bar"><i style={{ width: `${p.available ? (p.solved / p.available) * 100 : 0}%` }} /></div>
              </a>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

export function Pattern({ id, index }: { id: string; index: Index }) {
  const [p, err] = useData(() => loadPattern(id), id);
  if (err) return <Empty>No pattern called <code>{id}</code>.</Empty>;
  if (!p) return <Loading />;
  const mine = index.problems.filter((q) => q.pattern === id);
  const name = Object.fromEntries(index.patterns.map((x) => [x.id, x.name]));
  return (
    <article class="pattern">
      <header class="problem-head">
        <Kicker><a href={href('patterns')}>Patterns</a> · Tier {ROMAN[p.tier] ?? p.tier}</Kicker>
        <h1>{p.name}</h1>
        <p class="idea">{p.coreIdea}</p>
        <dl class="meta">
          <div><dt>Band</dt><dd><BandMark band={p.band} label /></dd></div>
          <div><dt>Solved</dt><dd>{p.solved} of {p.available}</dd></div>
          {p.avgHints != null && <div><dt>Avg. hints</dt><dd>{p.avgHints}</dd></div>}
          <div><dt>Builds on</dt><dd>{p.dependsOn.length ? p.dependsOn.map((d, i) => <>{i > 0 && ', '}<a href={href('patterns', d)}>{name[d] ?? d}</a></>) : 'nothing — a starting point'}</dd></div>
        </dl>
      </header>

      <section class="sec">
        <SectionHead label="My problems here" note={mine.length ? `${mine.length} in the notebook` : undefined} />
        {mine.length ? <ProblemRows problems={mine} /> : <Empty>None yet. The track decides when this pattern opens.</Empty>}
      </section>

      <section class="sec">
        <SectionHead label="Signals" note="what to look for in a statement" />
        <ul class="signals">{p.signals.map((s) => <li>{s}</li>)}</ul>
        {p.invariant && <p class="invariant"><span class="kicker">Invariant shape</span>{p.invariant}</p>}
      </section>

      {site.patternPage.filter((k) => p.brief[k]).map((k, i) => (
        <section class={`sec brief-${k}`}>
          <SectionHead n={i + 1} label={p.brief[k].label} />
          <Html html={p.brief[k].html} />
        </section>
      ))}
    </article>
  );
}
