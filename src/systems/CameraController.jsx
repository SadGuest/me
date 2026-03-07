import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { useGameState } from '../state/gameState';

const temp = new THREE.Vector3();

export function CameraController() {
  const camera = useThree((s) => s.camera);
  const snakes = useGameState((s) => s.snakes);

  useFrame(() => {
    const player = snakes.find((s) => s.isPlayer);
    if (!player?.segments?.length) return;
    const head = player.segments[0];
    const neck = player.segments[2] ?? player.segments[1] ?? head;
    const dir = new THREE.Vector3(head.x - neck.x, 0, head.z - neck.z).normalize();

    const distance = 18 + player.segments.length * 0.4;
    const desired = temp.set(head.x - dir.x * distance, head.y + 12, head.z - dir.z * distance);
    camera.position.lerp(desired, 0.03);

    const look = new THREE.Vector3(head.x + dir.x * 8, head.y + 1.8, head.z + dir.z * 8);
    camera.lookAt(camera.getWorldDirection(new THREE.Vector3()).lerp(look.sub(camera.position).normalize(), 0.05).add(camera.position));
  });

  return null;
}
