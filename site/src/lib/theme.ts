import { useState } from 'preact/hooks';

type Theme = 'system' | 'light' | 'dark';
const KEY = 'theme';

function get(): Theme {
  try { const t = localStorage.getItem(KEY); return t === 'light' || t === 'dark' ? t : 'system'; } catch { return 'system'; }
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(get);
  const cycle = () => {
    const next: Theme = theme === 'system' ? 'light' : theme === 'light' ? 'dark' : 'system';
    try { next === 'system' ? localStorage.removeItem(KEY) : localStorage.setItem(KEY, next); } catch { /* private mode */ }
    if (next === 'system') delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = next;
    setTheme(next);
  };
  return [theme, cycle] as const;
}
