import { useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useGameState } from '../state/gameState';
import { clampToWorld, sampleHeight, sampleNormal, WORLD_SIZE } from '../utils/terrain';

const FOOD_TARGET = 260;
const AI_COUNT = 8;
const personalities = ['aggressive', 'hunter', 'defensive', 'explorer'];

const randomPos = () => {
  const half = WORLD_SIZE / 2 - 5;
  const x = Math.random() * half * 2 - half;
  const z = Math.random() * half * 2 - half;
  return { x, y: sampleHeight(x, z), z };
};

const newFood = () => {
  const t = Math.random();
  const type = t > 0.96 ? 'ability' : t > 0.88 ? 'golden' : t > 0.72 ? 'rare' : 'common';
  return { id: crypto.randomUUID(), type, position: randomPos() };
};

const makeSnake = (id, isPlayer = false) => {
  const start = randomPos();
  const heading = Math.random() * Math.PI * 2;
  const speed = 16 + Math.random() * 8;
  const color = isPlayer ? '#ff6b6b' : `hsl(${Math.floor(Math.random() * 360)}deg, 80%, 62%)`;
  const length = isPlayer ? 14 : 12 + Math.floor(Math.random() * 8);
  const segments = Array.from({ length }, (_, i) => ({
    x: start.x - Math.cos(heading) * i * 0.9,
    y: sampleHeight(start.x - Math.cos(heading) * i * 0.9, start.z - Math.sin(heading) * i * 0.9),
    z: start.z - Math.sin(heading) * i * 0.9,
  }));

  return {
    id,
    isPlayer,
    color,
    speed,
    heading,
    targetHeading: heading,
    turnSpeed: 0.05,
    personality: personalities[Math.floor(Math.random() * personalities.length)],
    segments,
    alive: true,
  };
};

export function RuntimeSystem() {
  const {
    phase,
    startGame,
    foodItems,
    snakes,
    setFoodItems,
    setSnakes,
    mouseWorld,
    addScore,
    addEnergy,
    drainEnergy,
    growPlayer,
    triggerAbility,
    tickAbilities,
    setLeaderboard,
    pushEvent,
    tickEvents,
  } = useGameState();

  useEffect(() => {
    if (phase === 'menu') {
      startGame();
    }
  }, [phase, startGame]);

  useEffect(() => {
    if (phase !== 'playing') return;
    if (!snakes.length) {
      const generated = [makeSnake('player', true), ...Array.from({ length: AI_COUNT }, (_, i) => makeSnake(`ai-${i}`))];
      setSnakes(generated);
    }
    if (!foodItems.length) {
      setFoodItems(Array.from({ length: FOOD_TARGET }, newFood));
    }
  }, [phase, snakes.length, foodItems.length, setFoodItems, setSnakes]);

  useFrame((_, dt) => {
    if (phase !== 'playing' || !snakes.length) return;

    tickAbilities(dt);
    tickEvents(dt);
    drainEnergy(dt * 1.8);

    let updatedFood = [...foodItems];
    const updatedSnakes = snakes
      .filter((snake) => snake.alive)
      .map((snake) => {
        const head = snake.segments[0];
        let targetHeading = snake.targetHeading;

        if (snake.isPlayer) {
          targetHeading = Math.atan2(mouseWorld.z - head.z, mouseWorld.x - head.x);
        } else {
          const roll = Math.random();
          const nearestFood = updatedFood.reduce(
            (best, food) => {
              const d = (food.position.x - head.x) ** 2 + (food.position.z - head.z) ** 2;
              return d < best.d ? { d, food } : best;
            },
            { d: Infinity, food: null },
          ).food;

          const player = snakes[0];
          if (roll < 0.7 && nearestFood) {
            targetHeading = Math.atan2(nearestFood.position.z - head.z, nearestFood.position.x - head.x);
          } else if (roll < 0.9 && player) {
            const away = player.segments.length > snake.segments.length;
            const angle = Math.atan2(player.segments[0].z - head.z, player.segments[0].x - head.x);
            targetHeading = away ? angle + Math.PI : angle;
          } else {
            targetHeading += (Math.random() - 0.5) * 0.5;
          }
        }

        let deltaA = targetHeading - snake.heading;
        deltaA = Math.atan2(Math.sin(deltaA), Math.cos(deltaA));
        const turn = THREE.MathUtils.clamp(deltaA, -snake.turnSpeed, snake.turnSpeed);
        const heading = snake.heading + turn;

        const boosted = snake.isPlayer ? useGameState.getState().abilities.dash.active > 0 : false;
        const speed = (snake.isPlayer ? useGameState.getState().playerSpeed : snake.speed) + snake.segments.length * 0.05 + (boosted ? 20 : 0);

        const nx = head.x + Math.cos(heading) * speed * dt;
        const nz = head.z + Math.sin(heading) * speed * dt;
        const clamped = clampToWorld(new THREE.Vector3(nx, 0, nz));
        const normal = sampleNormal(clamped.x, clamped.z);
        const newHead = {
          x: clamped.x,
          y: sampleHeight(clamped.x, clamped.z) + normal.y * 0.05,
          z: clamped.z,
        };

        const spacing = 0.82;
        const targetLen = snake.isPlayer ? Math.floor(useGameState.getState().playerLength) : snake.segments.length;
        const segments = [newHead, ...snake.segments.slice(0, targetLen - 1)];
        for (let i = 1; i < segments.length; i += 1) {
          const prev = segments[i - 1];
          const cur = segments[i];
          const vx = cur.x - prev.x;
          const vz = cur.z - prev.z;
          const l = Math.hypot(vx, vz) || 1;
          cur.x = prev.x + (vx / l) * spacing;
          cur.z = prev.z + (vz / l) * spacing;
          cur.y = sampleHeight(cur.x, cur.z);
        }

        updatedFood = updatedFood.filter((food) => {
          const d = Math.hypot(food.position.x - newHead.x, food.position.z - newHead.z);
          if (d < 1.3) {
            if (snake.isPlayer) {
              const scoreMap = { common: 5, rare: 15, golden: 40, ability: 25 };
              const energyMap = { common: 3, rare: 8, golden: 20, ability: 12 };
              addScore(scoreMap[food.type]);
              addEnergy(energyMap[food.type]);
              if (food.type === 'ability') {
                const names = ['dash', 'magnet', 'shield', 'shockwave'];
                const name = names[Math.floor(Math.random() * names.length)];
                triggerAbility(name, 4, 10);
              }
              growPlayer(food.type === 'golden' ? 2 : 1);
              pushEvent({ position: food.position, label: `+${food.type === 'golden' ? 40 : 10}`, color: '#fff176' });
            }
            return false;
          }
          return true;
        });

        return {
          ...snake,
          heading,
          targetHeading,
          segments,
        };
      });

    for (let i = 0; i < updatedSnakes.length; i += 1) {
      const a = updatedSnakes[i];
      const headA = a.segments[0];
      for (let j = 0; j < updatedSnakes.length; j += 1) {
        if (i === j) continue;
        const b = updatedSnakes[j];
        for (let k = 2; k < b.segments.length; k += 1) {
          const s = b.segments[k];
          if (Math.hypot(headA.x - s.x, headA.z - s.z) < 0.7) {
            a.alive = false;
            b.segments.push(...a.segments.slice(-3));
            a.segments.forEach((seg, idx) => {
              if (idx % 2 === 0) updatedFood.push({ id: crypto.randomUUID(), type: 'common', position: seg });
            });
            pushEvent({ position: headA, label: 'BOOM', color: '#ff6b6b', ttl: 1.4 });
            break;
          }
        }
        if (!a.alive) break;
      }
    }

    const survivors = updatedSnakes.filter((s) => s.alive);
    while (updatedFood.length < FOOD_TARGET) updatedFood.push(newFood());

    setFoodItems(updatedFood);
    setSnakes(survivors);
    setLeaderboard(
      survivors
        .map((s) => ({ id: s.id, label: s.isPlayer ? 'You' : s.id, score: s.segments.length, color: s.color }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 8),
    );
  });

  return null;
}
