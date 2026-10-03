import { useEffect, useRef, useState } from 'preact/hooks';
import { search, type Hit } from '../lib/search';
import { go } from '../lib/router';
import { Diff } from './atoms';

/** ⌘K / "/" — jump to any problem by title, number, pattern, or a phrase from your own notes. */
export function Palette({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [q, setQ] = useState('');
  const [hits, setHits] = useState<Hit[]>([]);
  const [sel, setSel] = useState(0);
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => { if (open) { setQ(''); setHits([]); setSel(0); setTimeout(() => input.current?.focus(), 0); } }, [open]);
  useEffect(() => {
    let live = true;
    if (!q.trim()) { setHits([]); return; }
    search(q).then((h) => { if (live) { setHits(h); setSel(0); } });
    return () => { live = false; };
  }, [q]);

  if (!open) return null;
  const pick = (h?: Hit) => { if (h) { go('p', h.slug); onClose(); } };
  const onKey = (e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
    else if (e.key === 'ArrowDown') { e.preventDefault(); setSel((s) => Math.min(s + 1, hits.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setSel((s) => Math.max(s - 1, 0)); }
    else if (e.key === 'Enter') pick(hits[sel]);
  };

  return (
    <div class="palette-scrim" onClick={onClose}>
      <div class="palette" role="dialog" aria-label="Search" onClick={(e) => e.stopPropagation()}>
        <input
          ref={input}
          value={q}
          onInput={(e) => setQ((e.target as HTMLInputElement).value)}
          onKeyDown={onKey}
          placeholder="Search titles, numbers, patterns, your own notes…"
          aria-label="Search"
        />
        <ol class="palette-list">
          {hits.map((h, i) => (
            <li class={i === sel ? 'sel' : ''} onMouseEnter={() => setSel(i)} onClick={() => pick(h)}>
              <span class="num">{h.summary.id ?? ''}</span>
              <span class="t">{h.summary.title}</span>
              <span class="p">{h.summary.patternName}</span>
              <Diff d={h.summary.difficulty} />
            </li>
          ))}
          {q.trim() && !hits.length && <li class="none">Nothing matches “{q}”.</li>}
        </ol>
        <footer><kbd>↑</kbd><kbd>↓</kbd> move <kbd>↵</kbd> open <kbd>esc</kbd> close</footer>
      </div>
    </div>
  );
}
