import { useEffect, useState } from 'preact/hooks';
import type { Detail, Foundation, Index, PatternDetail } from './types';

const base = import.meta.env.BASE_URL;
const cache = new Map<string, Promise<unknown>>();

export function load<T>(rel: string): Promise<T> {
  if (!cache.has(rel)) {
    cache.set(rel, fetch(`${base}data/${rel}`).then((r) => {
      if (!r.ok) throw new Error(`${r.status} ${rel}`);
      return r.json();
    }));
  }
  return cache.get(rel) as Promise<T>;
}

export const loadIndex = () => load<Index>('index.json');
export const loadProblem = (slug: string) => load<Detail>(`problems/${slug}.json`);
export const loadPattern = (id: string) => load<PatternDetail>(`patterns/${id}.json`);
export const loadFoundations = () => load<Foundation[]>('foundations.json');
export const loadSearch = () => load<{ slug: string; signal: string; intuition: string; notes: string }[]>('search.json');

/** Suspends nothing: returns [data, error] and re-runs when the key changes. */
export function useData<T>(fn: () => Promise<T>, key: string): [T | null, Error | null] {
  const [state, set] = useState<[T | null, Error | null]>([null, null]);
  useEffect(() => {
    let live = true;
    set([null, null]);
    fn().then((d) => live && set([d, null]), (e) => live && set([null, e]));
    return () => { live = false; };
  }, [key]);
  return state;
}
