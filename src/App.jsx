import { GameCanvas } from './components/GameCanvas';
import { UIOverlay } from './ui/UIOverlay';

export default function App() {
  return (
    <div className="app-shell">
      <GameCanvas />
      <UIOverlay />
    </div>
  );
}
