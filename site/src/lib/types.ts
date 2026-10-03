export type Difficulty = 'Easy' | 'Medium' | 'Hard';
export type Band = 'untouched' | 'exposed' | 'working' | 'solid';

export interface Table { head: string[]; rows: string[][] }

export interface Summary {
  slug: string;
  id: number | null;
  title: string;
  difficulty: Difficulty | null;
  pattern: string;
  patternName: string;
  technique: string | null;
  status: string;
  stage: string | null;
  mode: string | null;
  path: string | null;
  solvedOn: string | null;
  firstTouched: string | null;
  hints: number;
  attempts: number;
  explanation: string | null;
  wrongGuesses: string[];
  verifiedUrl: string | null;
  verified: string | null;
  srs: { due: string | null; grade: string | null; reps: number; lapses: number };
  tags: string[];
  companies: string[];
  lists: string[];
  minutes: number | null;
  link: string;
  excerpt: string;
  sheet: { signal: string; intuition: string; complexity: { time: string; space: string } | null };
  langs: string[];
  defects: string[];
  activity: string[];
}

export interface Section { heading: string; note: string | null; kind: string; html: string; table?: Table; hasCode: boolean }

export interface Detail extends Summary {
  frontmatter: Record<string, unknown>;
  resources: { article?: string; youtube?: string } | null;
  sections: Record<string, Section>;
  other: { heading: string; html: string }[];
}

export interface PatternSummary {
  id: string;
  name: string;
  tier: number;
  dependsOn: string[];
  coreIdea: string;
  signals: string[];
  invariant: string;
  traps: string[];
  available: number;
  solved: number;
  inProgress: number;
  band: Band;
  avgHints: number | null;
  problems: string[];
}

export interface PatternDetail extends PatternSummary { brief: Record<string, { label: string; html: string }> }

export interface Index {
  built: string;
  mode: 'private' | 'public';
  available: number | null;
  problems: Summary[];
  patterns: PatternSummary[];
  activity: Record<string, number>;
  byDifficulty: Record<string, number>;
  errorProfile: {
    defects: { cls: string; count: number; slugs: string[] }[];
    confusions: { from: string; fromName: string; to: string; toName: string; times: number }[];
  } | null;
}

export interface Foundation {
  id: string;
  name: string;
  why: string;
  minutes: number;
  gates: string[];
  exercises: number;
  resources: { for: string; article?: string; youtube?: string }[];
  status: string;
  learnedOn: string | null;
  override: boolean;
  sections: { heading: string; html: string }[];
}
