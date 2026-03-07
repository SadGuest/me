import { Text } from '@react-three/drei';
import { useGameState } from '../state/gameState';

export function ParticleSystem() {
  const events = useGameState((s) => s.events).slice(0, 200);
  return (
    <group>
      {events.map((event) => (
        <group key={event.id} position={[event.position.x, event.position.y + (1.2 - event.ttl) * 2, event.position.z]}>
          <mesh>
            <sphereGeometry args={[0.2, 5, 5]} />
            <meshStandardMaterial color={event.color ?? '#ffffff'} emissive={event.color ?? '#ffffff'} emissiveIntensity={1.2} transparent opacity={Math.max(0.1, event.ttl)} />
          </mesh>
          <Text fontSize={0.8} color="white" anchorX="center" anchorY="middle" position={[0, 0.8, 0]}>
            {event.label ?? '+10'}
          </Text>
        </group>
      ))}
    </group>
  );
}
