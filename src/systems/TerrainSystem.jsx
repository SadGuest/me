import { useMemo } from 'react';
import * as THREE from 'three';
import { useGameState } from '../state/gameState';
import { sampleHeight, TERRAIN_SEGMENTS, WORLD_SIZE } from '../utils/terrain';

export function TerrainSystem() {
  const setMouseWorld = useGameState((s) => s.setMouseWorld);

  const terrain = useMemo(() => {
    const geometry = new THREE.PlaneGeometry(WORLD_SIZE, WORLD_SIZE, TERRAIN_SEGMENTS, TERRAIN_SEGMENTS);
    geometry.rotateX(-Math.PI / 2);
    const pos = geometry.attributes.position;
    for (let i = 0; i < pos.count; i += 1) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      pos.setY(i, sampleHeight(x, z));
    }
    geometry.computeVertexNormals();
    return geometry;
  }, []);

  return (
    <group>
      <mesh
        geometry={terrain}
        receiveShadow
        onPointerMove={(event) => {
          setMouseWorld({ x: event.point.x, y: event.point.y, z: event.point.z });
        }}
      >
        <meshStandardMaterial color="#4db35f" roughness={0.94} metalness={0.05} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -3, 0]}>
        <planeGeometry args={[WORLD_SIZE, WORLD_SIZE, 1, 1]} />
        <meshStandardMaterial color="#58b8e8" transparent opacity={0.42} emissive="#3eaee5" emissiveIntensity={0.2} />
      </mesh>
    </group>
  );
}
