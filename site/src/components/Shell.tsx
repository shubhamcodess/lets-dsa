import type { ComponentChildren } from 'preact';
import { useEffect, useState } from 'preact/hooks';
import { site } from '../lib/config';
import { href } from '../lib/router';
import { useTheme } from '../lib/theme';
import { warm } from '../lib/search';
import { Palette } from './Palette';

export function Shell({ section, built, mode, children }: { section: string; built?: string; mode?: string; children: ComponentChildren }) {
  const [theme, cycle] = useTheme();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const on = (e: KeyboardEvent) => {
      const typing = /INPUT|TEXTAREA|SELECT/.test((e.target as HTMLElement).tagName);
      if ((e.key === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !typing)) { e.preventDefault(); setOpen(true); }
    };
    addEventListener('keydown', on);
    return () => removeEventListener('keydown', on);
  }, []);

  return (
    <>
      <header class="mast">
        <div class="mast-in">
          <a class="brand" href={href()}>
            <span class="brand-mark">§</span>
            <span class="brand-name">{site.title}</span>
          </a>
          <nav class="nav" aria-label="Primary">
            {site.nav.map((n) => (
              <a href={href(n.route)} class={section === n.route ? 'on' : ''} aria-current={section === n.route ? 'page' : undefined}>{n.label}</a>
            ))}
          </nav>
          <div class="mast-tools">
            <button class="search-btn" onClick={() => { warm(); setOpen(true); }} onMouseEnter={warm} aria-label="Search">
              <span>Search</span><kbd>/</kbd>
            </button>
            <button class="theme-btn" data-t={theme} onClick={cycle} title={`Theme: ${theme}`} aria-label={`Theme: ${theme}`}>
              <svg viewBox="0 0 20 20" aria-hidden="true">
                <circle cx="10" cy="10" r="6.5" />
                {theme === 'system' && <path d="M10 3.5a6.5 6.5 0 0 1 0 13z" />}
              </svg>
            </button>
          </div>
        </div>
      </header>
      <main class="page">{children}</main>
      <footer class="colophon">
        <span>Set in Newsreader &amp; IBM Plex. Built mechanically from markdown — no model in the loop.</span>
        {built && <span>Compiled {built.slice(0, 10)}{mode === 'public' ? ' · public edition' : ''}</span>}
      </footer>
      <Palette open={open} onClose={() => setOpen(false)} />
    </>
  );
}
