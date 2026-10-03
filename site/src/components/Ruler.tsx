import { site } from '../lib/config';

/** The readiness ruler: a measured line, not a progress bar. Ticks at each threshold. */
export function Ruler({ solved }: { solved: number }) {
  const marks = site.readiness;
  const max = marks[marks.length - 1].at;
  const pct = (v: number) => `${Math.min(100, (v / max) * 100)}%`;
  const next = marks.find((m) => solved < m.at);
  return (
    <figure class="ruler">
      <div class="ruler-line">
        <div class="ruler-fill" style={{ width: pct(solved) }} />
        {Array.from({ length: max / 10 + 1 }, (_, i) => (
          <i class={`ruler-minor${(i * 10) % 50 === 0 ? ' mid' : ''}`} style={{ left: pct(i * 10) }} />
        ))}
        {marks.map((m) => (
          <div class={`ruler-mark${solved >= m.at ? ' passed' : ''}`} style={{ left: pct(m.at) }}>
            <span class="ruler-at">{m.at}</span>
            <span class="ruler-label">{m.label}</span>
          </div>
        ))}
        <div class="ruler-now" style={{ left: pct(solved) }}><span>{solved}</span></div>
      </div>
      <figcaption>
        {next
          ? <><strong>{next.at - solved}</strong> to {next.label.toLowerCase()} — {next.note}. A count is position, not readiness.</>
          : <>Past every threshold. Keep the revisits honest.</>}
      </figcaption>
    </figure>
  );
}
