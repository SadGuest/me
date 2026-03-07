import * as THREE from 'three';
import { useGameState } from '../state/gameState';

function SnakeMesh({ snake }) {
  return (
    <group>
      {snake.segments.map((segment, i) => (
        <mesh key={`${snake.id}-${i}`} position={[segment.x, segment.y + 0.5, segment.z]} castShadow>
          <sphereGeometry args={[Math.max(0.28, 0.8 - i * 0.01), 10, 10]} />
          <meshStandardMaterial color={snake.color} emissive={snake.color} emissiveIntensity={i === 0 ? 0.5 : 0.08} roughness={0.45} />
        </mesh>
      ))}
      <mesh position={[snake.segments[0].x, snake.segments[0].y + 0.8, snake.segments[0].z]}>
        <coneGeometry args={[0.34, 1, 6]} />
        <meshStandardMaterial color={new THREE.Color(snake.color).multiplyScalar(1.2)} emissive={snake.color} emissiveIntensity={0.4} />
      </mesh>
    </group>
  );
}

export function SnakeSystem() {
  const snakes = useGameState((s) => s.snakes);

  return (
    <group>
      {snakes.map((snake) => (
        <SnakeMesh key={snake.id} snake={snake} />
      ))}
    </group>
  );
}
