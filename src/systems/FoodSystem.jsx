import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import { useGameState } from '../state/gameState';

const foodStyle = {
  common: { color: '#82ff89', emissive: '#65f770', scale: 0.5 },
  rare: { color: '#7be2ff', emissive: '#50d6ff', scale: 0.7 },
  golden: { color: '#ffd95a', emissive: '#ffd010', scale: 0.86 },
  ability: { color: '#da82ff', emissive: '#c85cff', scale: 0.76 },
};

export function FoodSystem() {
  const foodItems = useGameState((s) => s.foodItems);
  const group = useRef();

  useFrame((state) => {
    if (!group.current) return;
    group.current.children.forEach((node, index) => {
      node.rotation.y += 0.02;
      node.position.y += Math.sin(state.clock.elapsedTime * 2 + index) * 0.004;
    });
  });

  return (
    <group ref={group}>
      {foodItems.map((food) => {
        const style = foodStyle[food.type];
        return (
          <mesh key={food.id} position={[food.position.x, food.position.y + 0.8, food.position.z]} castShadow>
            <icosahedronGeometry args={[style.scale, 0]} />
            <meshStandardMaterial color={style.color} emissive={style.emissive} emissiveIntensity={0.8} />
          </mesh>
        );
      })}
    </group>
  );
}
