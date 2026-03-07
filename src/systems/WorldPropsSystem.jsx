import { useMemo } from 'react';
import * as THREE from 'three';
import { sampleHeight, WORLD_SIZE } from '../utils/terrain';

function scatter(count, yOffset = 0) {
  const half = WORLD_SIZE / 2;
  return Array.from({ length: count }, () => {
    const x = Math.random() * WORLD_SIZE - half;
    const z = Math.random() * WORLD_SIZE - half;
    return [x, sampleHeight(x, z) + yOffset, z];
  });
}

export function WorldPropsSystem() {
  const trees = useMemo(() => scatter(420, 1), []);
  const rocks = useMemo(() => scatter(260, 0.4), []);
  const flowers = useMemo(() => scatter(700, 0.2), []);

  return (
    <group>
      {trees.map((p, i) => (
        <group key={`tree-${i}`} position={p}>
          <mesh castShadow>
            <cylinderGeometry args={[0.35, 0.5, 3.2, 6]} />
            <meshStandardMaterial color="#77563d" />
          </mesh>
          <mesh castShadow position={[0, 2.8, 0]}>
            <sphereGeometry args={[1.7, 7, 7]} />
            <meshStandardMaterial color="#2f9f42" emissive="#2f9f42" emissiveIntensity={0.04} />
          </mesh>
        </group>
      ))}
      {rocks.map((p, i) => (
        <mesh key={`rock-${i}`} position={p} castShadow>
          <dodecahedronGeometry args={[0.7 + Math.random() * 0.8, 0]} />
          <meshStandardMaterial color="#8c96a3" roughness={0.95} />
        </mesh>
      ))}
      {flowers.map((p, i) => (
        <mesh key={`flower-${i}`} position={p}>
          <sphereGeometry args={[0.08, 5, 5]} />
          <meshStandardMaterial color={new THREE.Color().setHSL(Math.random(), 0.8, 0.62)} emissive="#ffffff" emissiveIntensity={0.02} />
        </mesh>
      ))}
    </group>
  );
}
