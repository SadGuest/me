import { Canvas } from '@react-three/fiber';
import { Environment, Sky, Stars } from '@react-three/drei';
import { Suspense } from 'react';
import { TerrainSystem } from '../systems/TerrainSystem';
import { SnakeSystem } from '../systems/SnakeSystem';
import { FoodSystem } from '../systems/FoodSystem';
import { AISystem } from '../systems/AISystem';
import { AbilitySystem } from '../systems/AbilitySystem';
import { CameraController } from '../systems/CameraController';
import { ParticleSystem } from '../systems/ParticleSystem';
import { WorldPropsSystem } from '../systems/WorldPropsSystem';
import { RuntimeSystem } from '../systems/RuntimeSystem';

export function GameCanvas() {
  return (
    <Canvas shadows camera={{ position: [0, 24, 36], fov: 60 }}>
      <color attach="background" args={['#8fd3ff']} />
      <fog attach="fog" args={['#8fd3ff', 120, 520]} />
      <ambientLight intensity={0.48} />
      <directionalLight
        position={[140, 220, 100]}
        intensity={1.35}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />

      <Suspense fallback={null}>
        <Sky distance={450000} sunPosition={[1, 0.4, 0.5]} turbidity={7} />
        <Stars radius={500} depth={50} count={2000} factor={4} fade />
        <Environment preset="sunset" />

        <RuntimeSystem />
        <TerrainSystem />
        <WorldPropsSystem />
        <FoodSystem />
        <AISystem />
        <SnakeSystem />
        <AbilitySystem />
        <ParticleSystem />
        <CameraController />
      </Suspense>
    </Canvas>
  );
}
