import site from '../../config/site.config.json';
import content from '../../config/content.config.json';

export { site, content };

export const sectionRule = Object.fromEntries(content.sections.map((s) => [s.key, s])) as Record<
  string,
  (typeof content.sections)[number]
>;

/** Reveal order for recall mode: the distinct numeric `recall` steps, ascending. */
export const recallSteps = [...new Set(content.sections.map((s) => s.recall).filter((r): r is number => typeof r === 'number'))].sort((a, b) => a - b);

export const ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'];
