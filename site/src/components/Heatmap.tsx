import { fromIso, short, toIso, today } from '../lib/dates';

/** Sessions per day for the last N weeks, Monday-first columns. */
export function Heatmap({ activity, weeks = 26 }: { activity: Record<string, number>; weeks?: number }) {
  const end = fromIso(today());
  const start = new Date(end);
  start.setDate(end.getDate() - ((end.getDay() + 6) % 7) - (weeks - 1) * 7); // Monday, weeks ago
  const days: { iso: string; n: number; future: boolean }[] = [];
  for (let d = new Date(start); days.length < weeks * 7; d.setDate(d.getDate() + 1)) {
    const iso = toIso(d);
    days.push({ iso, n: activity[iso] ?? 0, future: iso > today() });
  }
  const level = (n: number) => (n === 0 ? 0 : n === 1 ? 1 : n <= 3 ? 2 : 3);
  const active = Object.keys(activity).filter((d) => d >= days[0].iso).length;
  return (
    <figure class="heat">
      <div class="heat-grid" style={{ gridTemplateColumns: `repeat(${weeks}, minmax(0, 13px))` }}>
        {days.map((d) => <i class={`l${level(d.n)}${d.future ? ' future' : ''}`} title={`${short(d.iso)} — ${d.n} problem${d.n === 1 ? '' : 's'} touched`} />)}
      </div>
      <figcaption>{active} active day{active === 1 ? '' : 's'} in the last {weeks} weeks</figcaption>
    </figure>
  );
}
