import type { ComponentChildren } from 'preact';
import type { Band, Difficulty } from '../lib/types';
import { site } from '../lib/config';

export function Diff({ d }: { d: Difficulty | null }) {
  if (!d) return null;
  return <span class={`diff diff-${d.toLowerCase()}`}><i />{d}</span>;
}

/** Four states drawn as a filling circle — reads at a glance without a legend. */
export function BandMark({ band, label = false }: { band: Band; label?: boolean }) {
  const fill = { untouched: 0, exposed: 0.25, working: 0.6, solid: 1 }[band];
  const r = 6, c = 2 * Math.PI * r;
  return (
    <span class={`band band-${band}`} title={site.bands[band]}>
      <svg viewBox="0 0 16 16" aria-hidden="true">
        <circle cx="8" cy="8" r={r} class="band-track" />
        <circle cx="8" cy="8" r={r} class="band-fill" stroke-dasharray={`${fill * c} ${c}`} transform="rotate(-90 8 8)" />
      </svg>
      {label && <span>{site.bands[band]}</span>}
    </span>
  );
}

/** Hints as five pips — the ladder has five rungs. */
export function Pips({ n, of = 5 }: { n: number; of?: number }) {
  return (
    <span class="pips" title={`${n} of ${of} hints`} aria-label={`${n} hints`}>
      {Array.from({ length: of }, (_, i) => <i class={i < n ? 'on' : ''} />)}
    </span>
  );
}

export function Kicker({ children }: { children: ComponentChildren }) {
  return <div class="kicker">{children}</div>;
}

export function SectionHead({ n, label, note, children }: { n?: number; label: string; note?: string | null; children?: ComponentChildren }) {
  return (
    <header class="sec-head">
      {n != null && <span class="sec-n">§ {String(n).padStart(2, '0')}</span>}
      <h2>{label}</h2>
      {note && <span class="sec-note">{note}</span>}
      {children && <span class="sec-actions">{children}</span>}
    </header>
  );
}

export function Html({ html, class: cls = 'prose' }: { html: string; class?: string }) {
  return <div class={cls} dangerouslySetInnerHTML={{ __html: html }} />;
}

export function Empty({ children }: { children: ComponentChildren }) {
  return <p class="empty">{children}</p>;
}

export function Loading() {
  return <div class="loading" aria-busy="true"><span /></div>;
}

export function Ext({ href, children }: { href: string; children: ComponentChildren }) {
  return <a class="ext" href={href} target="_blank" rel="noopener noreferrer">{children}<span aria-hidden="true">↗</span></a>;
}
