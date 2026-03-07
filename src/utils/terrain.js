import * as THREE from 'three';

export const WORLD_SIZE = 600;
export const TERRAIN_SEGMENTS = 240;

const hash = (x, z) => {
  const s = Math.sin(x * 127.1 + z * 311.7) * 43758.5453123;
  return s - Math.floor(s);
};

const valueNoise = (x, z) => {
  const ix = Math.floor(x);
  const iz = Math.floor(z);
  const fx = x - ix;
  const fz = z - iz;

  const a = hash(ix, iz);
  const b = hash(ix + 1, iz);
  const c = hash(ix, iz + 1);
  const d = hash(ix + 1, iz + 1);

  const ux = fx * fx * (3 - 2 * fx);
  const uz = fz * fz * (3 - 2 * fz);

  return THREE.MathUtils.lerp(
    THREE.MathUtils.lerp(a, b, ux),
    THREE.MathUtils.lerp(c, d, ux),
    uz,
  );
};

export const sampleHeight = (x, z) => {
  const nx = (x / WORLD_SIZE) * 8;
  const nz = (z / WORLD_SIZE) * 8;

  const hills = valueNoise(nx, nz) * 16;
  const mountains = Math.pow(valueNoise(nx * 0.35 + 19, nz * 0.35 + 53), 2.2) * 30;
  const valleys = -Math.pow(valueNoise(nx * 0.8 + 7, nz * 0.8 + 3), 1.8) * 10;
  const puddles = Math.sin(nx * 1.8) * Math.cos(nz * 1.7) * 1.2;

  return hills + mountains + valleys + puddles;
};

export const sampleNormal = (x, z) => {
  const e = 0.6;
  const hL = sampleHeight(x - e, z);
  const hR = sampleHeight(x + e, z);
  const hD = sampleHeight(x, z - e);
  const hU = sampleHeight(x, z + e);
  return new THREE.Vector3(hL - hR, 2 * e, hD - hU).normalize();
};

export const clampToWorld = (v) => {
  const half = WORLD_SIZE / 2 - 2;
  return new THREE.Vector3(
    THREE.MathUtils.clamp(v.x, -half, half),
    v.y,
    THREE.MathUtils.clamp(v.z, -half, half),
  );
};
