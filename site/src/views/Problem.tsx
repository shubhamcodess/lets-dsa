import { useEffect, useState } from 'preact/hooks';
import type { Detail, Index } from '../lib/types';
import { loadProblem, useData } from '../lib/data';
import { recallSteps, sectionRule, site } from '../lib/config';
import { href } from '../lib/router';
import { relative, short, isDue } from '../lib/dates';
import { Diff, Empty, Ext, Html, Kicker, Loading, Pips, SectionHead } from '../components/atoms';

export function Problem({ slug, index }: { slug: string; index: Index }) {
  const [p, err] = useData(() => loadProblem(slug), slug);
  const [recall, setRecall] = useState(() => location.hash.includes('recall'));
  const [step, setStep] = useState(0);

  useEffect(() => { setStep(0); }, [slug, recall]);
  useEffect(() => {
    if (!recall) return;
    const on = (e: KeyboardEvent) => {
      if (e.key !== ' ' || /INPUT|TEXTAREA|SELECT/.test((e.target as HTMLElement).tagName)) return;
      e.preventDefault(); // also stops Space from re-pressing a focused button
      (document.activeElement as HTMLElement | null)?.blur();
      setStep((s) => Math.min(s + 1, recallSteps.length));
    };
    addEventListener('keydown', on);
    return () => removeEventListener('keydown', on);
  }, [recall]);

  if (err) return <Empty>Couldn’t load <code>{slug}</code>. Is it in <code>questions/</code>?</Empty>;
  if (!p) return <Loading />;

  const visible = (key: string) => {
    if (!recall) return true;
    const r = sectionRule[key]?.recall;
    if (r === 'show') return true;
    return typeof r === 'number' && recallSteps.indexOf(r) < step;
  };
  const nextStep = recallSteps[step];
  const nextLabels = site.problemPage.sections
    .filter((k) => sectionRule[k]?.recall === nextStep && p.sections[k])
    .map((k) => sectionRule[k].label);

  const order = site.problemPage.sections.filter((k) => k === 'other' ? p.other.length : p.sections[k]);
  const siblings = index.problems.filter((q) => q.pattern === p.pattern && q.slug !== p.slug);

  return (
    <article class={`problem${recall ? ' recall' : ''}`}>
      <header class="problem-head">
        <Kicker>
          <a href={href('patterns', p.pattern)}>{p.patternName}</a>
          {p.technique && <> · {p.technique}</>}
        </Kicker>
        <h1><span class="num">{p.id != null ? `${p.id}.` : ''}</span> {p.title}</h1>
        <Meta p={p} />
        {(p.tags.length > 0 || p.companies.length > 0) && (
          <p class="tags">
            {p.tags.map((t) => <span class="tag">{t}</span>)}
            {p.companies.map((c) => <span class="tag co">{c}</span>)}
          </p>
        )}
        <div class="actions">
          <Ext href={p.link}>Open on LeetCode</Ext>
          {p.verifiedUrl && <Ext href={p.verifiedUrl}>My accepted submission</Ext>}
          {p.resources?.article && <Ext href={p.resources.article}>Article</Ext>}
          {p.resources?.youtube && <Ext href={p.resources.youtube}>Walkthrough</Ext>}
          <button class={`btn recall-btn${recall ? ' on' : ''}`} onClick={() => setRecall(!recall)} aria-pressed={recall}>
            {recall ? 'Exit recall' : 'Recall mode'}
          </button>
        </div>
      </header>

      {recall && (
        <div class="recall-bar">
          <p>Read the problem. Before revealing, say out loud: the pattern, the signal that selects it, the invariant, and the optimal’s cost.</p>
          {nextStep != null
            ? <button class="btn" onClick={() => setStep(step + 1)}>Reveal {nextLabels.join(' & ').toLowerCase() || 'next'} <kbd>space</kbd></button>
            : <span class="done">Everything revealed.</span>}
          {step > 0 && <button class="btn ghost" onClick={() => setStep(0)}>Hide again</button>}
        </div>
      )}

      <div class="problem-body">
        {order.map((k, i) => {
          if (k === 'other') {
            return p.other.map((o) => (
              <section class="sec"><SectionHead label={o.heading} /><Html html={o.html} /></section>
            ));
          }
          const s = p.sections[k];
          const rule = sectionRule[k];
          const shown = visible(k);
          return (
            <section class={`sec sec-${k} kind-${s.kind}${shown ? '' : ' veiled'}`} id={k}>
              <SectionHead n={i + 1} label={rule?.label ?? s.heading} note={s.note} />
              {shown ? <Html html={s.html} class={`prose kind-${s.kind}`} /> : <div class="veil" aria-hidden="true" />}
            </section>
          );
        })}
      </div>

      {siblings.length > 0 && (
        <aside class="siblings">
          <Kicker>Also in {p.patternName}</Kicker>
          <ul>{siblings.map((q) => <li><a href={href('p', q.slug)}>{q.title}</a> <Diff d={q.difficulty} /></li>)}</ul>
        </aside>
      )}
    </article>
  );
}

function Meta({ p }: { p: Detail }) {
  const cells: Record<string, () => preact.JSX.Element | null> = {
    difficulty: () => <div><dt>Difficulty</dt><dd><Diff d={p.difficulty} /></dd></div>,
    status: () => <div><dt>Status</dt><dd>{p.status === 'solved' ? 'Solved' : 'In progress'}{p.path === 'express' && ' · express'}{p.mode === 'review-only' && ' · review-only'}</dd></div>,
    hints: () => <div><dt>Hints</dt><dd><Pips n={p.hints} /> {p.hints}/5</dd></div>,
    attempts: () => <div><dt>Attempts</dt><dd>{p.attempts}</dd></div>,
    solvedOn: () => <div><dt>Solved</dt><dd>{short(p.solvedOn)}</dd></div>,
    due: () => p.srs.due ? <div><dt>Next recall</dt><dd class={isDue(p.srs.due) ? 'due' : ''}>{relative(p.srs.due)}{p.srs.grade && <small> · last {p.srs.grade}</small>}</dd></div> : null,
    language: () => p.langs.length ? <div><dt>Language</dt><dd>{p.langs.join(', ')}</dd></div> : null,
    sheets: () => p.lists.length ? <div><dt>Curated in</dt><dd>{p.lists.length} sheet{p.lists.length > 1 ? 's' : ''}</dd></div> : null,
  };
  return <dl class="meta">{site.problemPage.meta.map((m) => cells[m]?.())}</dl>;
}
