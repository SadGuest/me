import { create } from 'zustand';

const abilityDefaults = {
  dash: { cooldown: 0, active: 0 },
  magnet: { cooldown: 0, active: 0 },
  shield: { cooldown: 0, active: 0 },
  shockwave: { cooldown: 0, active: 0 },
};

export const useGameState = create((set, get) => ({
  phase: 'menu',
  score: 0,
  energy: 100,
  playerLength: 14,
  playerSpeed: 24,
  mouseWorld: { x: 0, y: 0, z: 0 },
  abilities: abilityDefaults,
  leaderboard: [],
  events: [],
  foodItems: [],
  snakes: [],

  startGame: () =>
    set({
      phase: 'playing',
      score: 0,
      energy: 100,
      playerLength: 14,
      playerSpeed: 24,
      abilities: abilityDefaults,
      events: [],
      foodItems: [],
      snakes: [],
    }),
  pauseGame: () => set({ phase: 'paused' }),
  resumeGame: () => set({ phase: 'playing' }),
  gameOver: () => set({ phase: 'gameover' }),

  setMouseWorld: (mouseWorld) => set({ mouseWorld }),
  addScore: (delta) => set((s) => ({ score: s.score + delta })),
  addEnergy: (delta) => set((s) => ({ energy: Math.min(100, Math.max(0, s.energy + delta)) })),
  drainEnergy: (delta) => {
    const energy = Math.max(0, get().energy - delta);
    set({ energy, playerSpeed: 14 + (energy / 100) * 14 });
    if (energy <= 0) {
      set((s) => ({ playerLength: Math.max(6, s.playerLength - 0.02) }));
    }
  },
  growPlayer: (amount = 1) => set((s) => ({ playerLength: s.playerLength + amount })),

  triggerAbility: (name, duration, cooldown) =>
    set((s) => ({
      abilities: {
        ...s.abilities,
        [name]: { cooldown, active: duration },
      },
    })),
  tickAbilities: (dt) =>
    set((s) => {
      const abilities = { ...s.abilities };
      Object.keys(abilities).forEach((key) => {
        abilities[key] = {
          cooldown: Math.max(0, abilities[key].cooldown - dt),
          active: Math.max(0, abilities[key].active - dt),
        };
      });
      return { abilities };
    }),

  setLeaderboard: (leaderboard) => set({ leaderboard }),
  setFoodItems: (foodItems) => set({ foodItems }),
  setSnakes: (snakes) => set({ snakes }),

  pushEvent: (event) =>
    set((s) => ({
      events: [...s.events.slice(-32), { ...event, id: crypto.randomUUID(), ttl: event.ttl ?? 1.2 }],
    })),
  tickEvents: (dt) =>
    set((s) => ({
      events: s.events
        .map((event) => ({ ...event, ttl: event.ttl - dt }))
        .filter((event) => event.ttl > 0),
    })),
}));
