import type { Index, Summary } from '../lib/types';
import { ROMAN, site } from '../lib/config';
import { href } from '../lib/router';
import { isDue, relative, short, today, daysBetween } from '../lib/dates';
import { BandMark, Diff, Empty, Kicker, Pips, SectionHead } from '../components/atoms';
import { Ruler } from '../components/Ruler';
import { Heatmap } from '../components/Heatmap';

export function Overview({ index }: { index: Index }) {
  const solved = index.problems.filter((p) => p.status === 'solved');
  const touched = index.patterns.filter((p) => p.solved > 0).length;
  const widgets: Record<string, () => preact.JSX.Element | null> = {
    readiness: () => <Readiness index={index} solved={solved} touched={touched} />,
    due: () => <Due problems={solved} />,
    patternMap: () => <PatternMap index={index} />,
    errorProfile: () => <ErrorProfile index={index} />,
    activity: () => (
      <section class="block">
        <SectionHead label="Practice" note="days with a problem touched" />
        <Heatmap activity={index.activity} />
      </section>
    ),
    recent: () => <Recent problems={solved} />,
  };
  return <div class="overview">{site.overview.map((w) => widgets[w]?.())}</div>;
}

function Readiness({ index, solved, touched }: { index: Index; solved: Summary[]; touched: number }) {
  const hints = solved.length ? solved.reduce((a, p) => a + p.hints, 0) / solved.length : 0;
  const clean = solved.filter((p) => p.hints === 0).length;
  return (
    <section class="hero">
      <Kicker>The notebook · {short(today())}</Kicker>
      <h1 class="hero-line">
        <span class="hero-num">{solved.length}</span> solved, across <em>{touched}</em> of {index.patterns.length} patterns.
      </h1>
      <p class="hero-sub">{site.subtitle}</p>
      <Ruler solved={solved.length} />
      <dl class="figures">
        <div><dt>Easy</dt><dd><Diff d="Easy" /> {index.byDifficulty.Easy ?? 0}</dd></div>
        <div><dt>Medium</dt><dd><Diff d="Medium" /> {index.byDifficulty.Medium ?? 0}</dd></div>
        <div><dt>Hard</dt><dd><Diff d="Hard" /> {index.byDifficulty.Hard ?? 0}</dd></div>
        <div><dt>Avg. hints</dt><dd>{hints.toFixed(1)}<small> / 5</small></dd></div>
        <div><dt>Cold solves</dt><dd>{clean}<small> with no hint</small></dd></div>
      </dl>
    </section>
  );
}

function Due({ problems }: { problems: Summary[] }) {
  const t = today();
  const upcoming = problems
    .filter((p) => p.srs.due && daysBetween(t, p.srs.due) <= 7)
    .sort((a, b) => a.srs.due!.localeCompare(b.srs.due!));
  const due = upcoming.filter((p) => isDue(p.srs.due));
  const next = problems.filter((p) => p.srs.due && p.srs.due > t).sort((a, b) => a.srs.due!.localeCompare(b.srs.due!))[0];
  return (
    <section class="block">
      <SectionHead label="Due for recall" note={due.length ? `${due.length} today` : 'nothing overdue'}>
        {due.length > 0 && <a class="btn" href={href('revise', 'due')}>Start recall →</a>}
      </SectionHead>
      {upcoming.length ? (
        <ul class="due-list">
          {upcoming.map((p) => (
            <li class={isDue(p.srs.due) ? 'is-due' : ''}>
              <a href={href('p', p.slug)}>
                <span class="when">{relative(p.srs.due)}</span>
                <span class="t">{p.title}</span>
                <span class="p">{p.patternName}</span>
              </a>
            </li>
          ))}
        </ul>
      ) : (
        <Empty>Nothing due this week.{next && <> Next up: <a href={href('p', next.slug)}>{next.title}</a>, {relative(next.srs.due)}.</>}</Empty>
      )}
    </section>
  );
}

function PatternMap({ index }: { index: Index }) {
  const tiers = [...new Set(index.patterns.map((p) => p.tier))].sort();
  return (
    <section class="block">
      <SectionHead label="The map" note="twenty patterns in dependency order — a tier leans on the ones before it">
        <a class="btn ghost" href={href('patterns')}>All patterns →</a>
      </SectionHead>
      <div class="map">
        {tiers.map((t) => (
          <div class="map-tier">
            <div class="map-tier-n">Tier {ROMAN[t] ?? t}</div>
            {index.patterns.filter((p) => p.tier === t).map((p) => (
              <a class={`map-cell band-${p.band}`} href={href('patterns', p.id)}>
                <BandMark band={p.band} />
                <span class="map-name">{p.name}</span>
                <span class="map-count">{p.solved}<small>/{p.available}</small></span>
              </a>
            ))}
          </div>
        ))}
      </div>
      <p class="legend">
        {(['untouched', 'exposed', 'working', 'solid'] as const).map((b) => <BandMark band={b} label />)}
      </p>
    </section>
  );
}

function ErrorProfile({ index }: { index: Index }) {
  const ep = index.errorProfile;
  if (!ep) return null;
  const solved = index.problems.filter((p) => p.status === 'solved').length;
  const max = Math.max(1, ...ep.defects.map((d) => d.count));
  return (
    <section class="block">
      <SectionHead label="How I go wrong" note="from my own defect tables and first guesses" />
      {solved < 5 && <p class="caveat">Thin data — {solved} problems. Read this as a hint, not a profile.</p>}
      <div class="two-col">
        <div>
          <Kicker>Defect classes</Kicker>
          {ep.defects.length ? (
            <ul class="bars">
              {ep.defects.map((d) => (
                <li>
                  <span class="bar-label mono">{d.cls}</span>
                  <span class="bar"><i style={{ width: `${(d.count / max) * 100}%` }} /></span>
                  <span class="bar-n">{d.count}</span>
                </li>
              ))}
            </ul>
          ) : <Empty>No defects recorded yet.</Empty>}
        </div>
        <div>
          <Kicker>Pattern confusions</Kicker>
          {ep.confusions.length ? (
            <ul class="confusions">
              {ep.confusions.map((c) => (
                <li>Called it <a href={href('patterns', c.from)}>{c.fromName}</a> — it was <a href={href('patterns', c.to)}>{c.toName}</a>{c.times > 1 && <b> ×{c.times}</b>}</li>
              ))}
            </ul>
          ) : <Empty>No wrong first guesses recorded.</Empty>}
        </div>
      </div>
    </section>
  );
}

function Recent({ problems }: { problems: Summary[] }) {
  return (
    <section class="block">
      <SectionHead label="Recently solved">
        <a class="btn ghost" href={href('problems')}>All problems →</a>
      </SectionHead>
      <ProblemRows problems={problems.slice(0, 8)} />
    </section>
  );
}

export function ProblemRows({ problems }: { problems: Summary[] }) {
  if (!problems.length) return <Empty>No problems match.</Empty>;
  return (
    <ol class="rows">
      {problems.map((p) => (
        <li>
          <a href={href('p', p.slug)}>
            <span class="num">{p.id ?? ''}</span>
            <span class="t">
              {p.title}
              {p.status !== 'solved' && <span class="tag">in progress</span>}
              {p.mode === 'review-only' && <span class="tag">review-only</span>}
            </span>
            <span class="p">{p.patternName}{p.technique && <small> · {p.technique}</small>}</span>
            <Diff d={p.difficulty} />
            <Pips n={p.hints} />
            <span class={`when${isDue(p.srs.due) ? ' due' : ''}`}>{p.solvedOn ? short(p.solvedOn) : '—'}</span>
          </a>
        </li>
      ))}
    </ol>
  );
}
