import { useEffect, useState } from 'preact/hooks';

/** Hash routes keep the build host-agnostic — no server rewrites, no 404.html trick. */
const read = () => decodeURIComponent(location.hash.replace(/^#\/?/, '')).split('?')[0].split('/').filter(Boolean);

export function useRoute() {
  const [route, set] = useState(read);
  useEffect(() => {
    const on = () => { set(read()); window.scrollTo(0, 0); };
    addEventListener('hashchange', on);
    return () => removeEventListener('hashchange', on);
  }, []);
  return route;
}

export const href = (...parts: string[]) => `#/${parts.filter(Boolean).join('/')}`;
export const go = (...parts: string[]) => { location.hash = href(...parts); };
