import { useState } from 'preact/hooks';
import type { Index } from '../lib/types';
import { loadFoundations, useData } from '../lib/data';
import { href } from '../lib/router';
import { short } from '../lib/dates';
import { Empty, Ext, Html, Kicker, Loading } from '../components/atoms';

const STATUS: Record<string, string> = { learned: 'Learned', in_progress: 'In progress', not_started: 'Not started' };

export function Foundations({ index }: { index: Index }) {
  const [list, err] = useData(loadFoundations, 'foundations');
  const [open, setOpen] = useState<string | null>(null);
  if (err) return <Empty>Couldn’t load foundations.</Empty>;
  if (!list) return <Loading />;
  const name = Object.fromEntries(index.patterns.map((p) => [p.id, p.name]));
  const learned = list.filter((f) => f.status === 'learned').length;
  const minutes = list.filter((f) => f.status !== 'learned').reduce((a, f) => a + f.minutes, 0);
  return (
    <div class="foundations">
      <header class="page-head">
        <Kicker>Before the loop</Kicker>
        <h1>Foundations</h1>
        <p class="lede">{learned} of {list.length} learned. About {Math.round(minutes / 60)} hours of groundwork left, and each topic opens the patterns that lean on it.</p>
      </header>
      <ol class="flist">
        {list.map((f) => (
          <li class={`f f-${f.status}`}>
            <button class="f-head" onClick={() => setOpen(open === f.id ? null : f.id)} aria-expanded={open === f.id}>
              <span class="f-n mono">{f.id.slice(0, 2)}</span>
              <span class="f-name">{f.name}</span>
              <span class="f-status">{STATUS[f.status] ?? f.status}{f.learnedOn && ` · ${short(f.learnedOn)}`}</span>
              <span class="f-min mono">{f.minutes}m</span>
            </button>
            {open === f.id && (
              <div class="f-body">
                <p class="why">{f.why}</p>
                {f.gates.length > 0 && (
                  <p class="gates">Opens {f.gates.map((g, i) => <>{i > 0 && ', '}<a href={href('patterns', g)}>{name[g] ?? g}</a></>)}</p>
                )}
                {f.sections.map((s) => <section><h3>{s.heading}</h3><Html html={s.html} /></section>)}
                {f.resources.length > 0 && (
                  <details>
                    <summary>{f.resources.length} free resources</summary>
                    <ul class="res">
                      {f.resources.map((r) => (
                        <li>{r.for} {r.article && <Ext href={r.article}>article</Ext>} {r.youtube && <Ext href={r.youtube}>video</Ext>}</li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
