import { render } from 'preact';
import './styles/fonts.css';
import './styles/tokens.css';
import './styles/app.css';

import { loadIndex, useData } from './lib/data';
import { useRoute } from './lib/router';
import { Shell } from './components/Shell';
import { Empty, Loading } from './components/atoms';
import { Overview } from './views/Overview';
import { Problems } from './views/Problems';
import { Problem } from './views/Problem';
import { Patterns, Pattern } from './views/Patterns';
import { Revise } from './views/Revise';
import { Sheet } from './views/Sheet';
import { Foundations } from './views/Foundations';

function App() {
  const [section, arg] = useRoute();
  const [index, err] = useData(loadIndex, 'index');

  const view = () => {
    if (err) return <Empty>No data yet. Run <code>npm run data</code> inside <code>site/</code>.</Empty>;
    if (!index) return <Loading />;
    switch (section ?? '') {
      case '': return <Overview index={index} />;
      case 'problems': return <Problems index={index} />;
      case 'p': return <Problem key={arg} slug={arg} index={index} />;
      case 'patterns': return arg ? <Pattern key={arg} id={arg} index={index} /> : <Patterns index={index} />;
      case 'revise': return <Revise index={index} deck={arg} />;
      case 'sheet': return <Sheet index={index} />;
      case 'foundations': return <Foundations index={index} />;
      default: return <Empty>Nothing lives at this address. <a href="#/">Back to the overview.</a></Empty>;
    }
  };

  const nav = section === 'p' ? 'problems' : section ?? '';
  return <Shell section={nav} built={index?.built} mode={index?.mode}>{view()}</Shell>;
}

render(<App />, document.getElementById('app')!);
