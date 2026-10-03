import { useEffect, useMemo, useState } from 'preact/hooks';
import type { Detail, Index, Summary } from '../lib/types';
import { loadProblem } from '../lib/data';
import { isDue } from '../lib/dates';
import { go, href } from '../lib/router';
import { Diff, Html, Kicker, Loading } from '../components/atoms';

type Verdict = 'recalled' | 'shaky' | 'missed';
const KEY = 'revise-log';

/**
 * Flashcards over my own problems. Front: the problem as I first saw it. Back: my signal,
 * intuition and cost. The verdict is kept in this browser only — the real schedule lives in
 * the question files and is updated by schedule.py, not by a static page.
 */
export function Revise({ index, deck: deckKey }: { index: Index; deck?: string }) {
  const solved = index.problems.filter((p) => p.status === 'solved');
  const decks: Record<string, [string, Summary[]]> = {
    due: ['Due today', solved.filter((p) => isDue(p.srs.due))],
    all: ['Everything solved', solved],
    shaky: ['Needed hints', solved.filter((p) => p.hints > 0 || p.attempts > 1)],
    ...Object.fromEntries(index.patterns.filter((p) => p.solved).map((p) => [p.id, [p.name, solved.filter((q) => q.pattern === p.id)]])),
  };

  if (!deckKey || !decks[deckKey]) {
    return (
      <div class="revise">
        <header class="page-head">
          <Kicker>Active recall</Kicker>
          <h1>Revise</h1>
          <p class="lede">See the problem cold. Say the pattern, the signal, the invariant and the optimal’s cost — then turn the card.</p>
        </header>
        <div class="decks">
          {Object.entries(decks).map(([k, [label, list]]) => (
            <a class={`deck${list.length ? '' : ' empty'}`} href={list.length ? href('revise', k) : undefined}>
              <span class="deck-n">{list.length}</span>
              <span class="deck-l">{label}</span>
            </a>
          ))}
        </div>
        <p class="note">Before an interview, the <a href={href('sheet')}>cheat sheet</a> is the one-page version.</p>
      </div>
    );
  }
  return <Session key={deckKey} title={decks[deckKey][0]} cards={decks[deckKey][1]} />;
}

function Session({ title, cards }: { title: string; cards: Summary[] }) {
  const order = useMemo(() => shuffle(cards.map((c) => c.slug)), [cards]);
  const [i, setI] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [tally, setTally] = useState<Record<Verdict, number>>({ recalled: 0, shaky: 0, missed: 0 });
  const [card, setCard] = useState<Detail | null>(null);

  useEffect(() => {
    if (i >= order.length) return;
    setCard(null);
    setFlipped(false);
    loadProblem(order[i]).then(setCard);
    if (order[i + 1]) void loadProblem(order[i + 1]); // prefetch the next card
  }, [i]);

  const rate = (v: Verdict) => {
    setTally((t) => ({ ...t, [v]: t[v] + 1 }));
    try {
      const log = JSON.parse(localStorage.getItem(KEY) ?? '{}');
      log[order[i]] = { v, at: new Date().toISOString().slice(0, 10) };
      localStorage.setItem(KEY, JSON.stringify(log));
    } catch { /* storage unavailable — the session still works */ }
    setI(i + 1);
  };

  useEffect(() => {
    const on = (e: KeyboardEvent) => {
      if (e.key === ' ') { e.preventDefault(); setFlipped(true); }
      if (!flipped) return;
      if (e.key === '1') rate('recalled');
      if (e.key === '2') rate('shaky');
      if (e.key === '3') rate('missed');
    };
    addEventListener('keydown', on);
    return () => removeEventListener('keydown', on);
  });

  if (i >= order.length) {
    return (
      <div class="revise done">
        <Kicker>{title}</Kicker>
        <h1>Deck finished.</h1>
        <p class="lede">{tally.recalled} recalled · {tally.shaky} shaky · {tally.missed} missed</p>
        {tally.missed + tally.shaky > 0 && <p>Log the misses in the notebook with a revisit — that is what moves the real schedule.</p>}
        <div class="actions"><button class="btn" onClick={() => go('revise')}>Choose another deck</button></div>
      </div>
    );
  }

  return (
    <div class="revise">
      <div class="session-bar">
        <a href={href('revise')}>← Decks</a>
        <span>{title}</span>
        <span class="mono">{i + 1} / {order.length}</span>
      </div>
      {!card ? <Loading /> : (
        <article class={`card${flipped ? ' flipped' : ''}`}>
          <header>
            <Kicker>{card.id ? `#${card.id}` : ''}</Kicker>
            <h1>{card.title}</h1>
            <Diff d={card.difficulty} />
          </header>
          {card.sections.problem && <Html html={card.sections.problem.html} />}
          {card.sections.examples && <Html html={card.sections.examples.html} />}

          {!flipped ? (
            <div class="prompt">
              <ol>
                <li>Which pattern — and which words in the statement select it?</li>
                <li>What invariant does the optimal hold?</li>
                <li>Brute → optimal: time and space.</li>
              </ol>
              <button class="btn" onClick={() => setFlipped(true)}>Turn the card <kbd>space</kbd></button>
            </div>
          ) : (
            <div class="back">
              <div class="answer-pattern"><span class="kicker">Pattern</span>{card.patternName}{card.technique && <small> · {card.technique}</small>}</div>
              {card.sections.signal && <><h3>Signal</h3><Html html={card.sections.signal.html} /></>}
              {card.sections.intuition && <><h3>Intuition</h3><Html html={card.sections.intuition.html} /></>}
              {card.sections.ladder && <><h3>The ladder</h3><Html html={card.sections.ladder.html} /></>}
              <div class="rate">
                <button class="btn r1" onClick={() => rate('recalled')}>Recalled <kbd>1</kbd></button>
                <button class="btn r2" onClick={() => rate('shaky')}>Shaky <kbd>2</kbd></button>
                <button class="btn r3" onClick={() => rate('missed')}>Missed <kbd>3</kbd></button>
                <a class="btn ghost" href={href('p', card.slug)}>Full notes</a>
              </div>
            </div>
          )}
        </article>
      )}
    </div>
  );
}

function shuffle<T>(a: T[]) {
  const b = [...a];
  for (let i = b.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [b[i], b[j]] = [b[j], b[i]]; }
  return b;
}
