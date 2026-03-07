import { motion, AnimatePresence } from 'framer-motion';
import { useGameState } from '../state/gameState';

function AbilitySlot({ name, data }) {
  const active = data.active > 0;
  const cooldown = Math.max(0, data.cooldown);
  return (
    <div className={`ability-slot ${active ? 'active' : ''}`}>
      <span>{name}</span>
      <small>{cooldown > 0 ? cooldown.toFixed(1) : 'Ready'}</small>
    </div>
  );
}

export function UIOverlay() {
  const { phase, score, energy, abilities, leaderboard } = useGameState();

  return (
    <div className="ui-layer">
      <AnimatePresence>
        {phase === 'menu' && (
          <motion.div className="menu-card" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}>
            <h1>Cartoon Open World Snake</h1>
            <p>Explore hills, collect glowing fruit, and outgrow rival snakes.</p>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div className="hud" initial={{ y: 16, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
        <div className="panel">
          <h3>Score</h3>
          <p>{score}</p>
        </div>
        <div className="panel energy">
          <h3>Energy</h3>
          <div className="bar">
            <motion.div className="fill" animate={{ width: `${energy}%` }} transition={{ type: 'spring', stiffness: 80 }} />
          </div>
          <small>{Math.round(energy)}%</small>
        </div>
        <div className="panel minimap">
          <h3>Minimap</h3>
          <div className="map-dot" />
        </div>
      </motion.div>

      <div className="bottom-row">
        <div className="abilities panel">
          <h3>Abilities</h3>
          <div className="ability-grid">
            {Object.entries(abilities).map(([name, data]) => (
              <AbilitySlot key={name} name={name} data={data} />
            ))}
          </div>
        </div>

        <div className="panel leaderboard">
          <h3>Leaderboard</h3>
          {leaderboard.map((entry, i) => (
            <p key={entry.id} style={{ color: entry.color }}>
              {i + 1}. {entry.label} — {entry.score}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}
