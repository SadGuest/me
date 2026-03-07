from __future__ import annotations

import math

from ursina import Entity, Mesh, color, Vec3

from game.core.settings import Settings

try:
    from noise import pnoise2
except Exception:  # pragma: no cover
    pnoise2 = None


class TerrainSystem:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.entity = self._build_terrain_entity()

    def _sample_noise(self, x: float, z: float) -> float:
        scale = self.settings.terrain_scale
        if pnoise2:
            return pnoise2(x * scale, z * scale, octaves=4, persistence=0.55, lacunarity=2.0)
        return (
            math.sin(x * scale * 1.7) * 0.45
            + math.cos(z * scale * 1.3) * 0.35
            + math.sin((x + z) * scale * 0.7) * 0.2
        )

    def get_height(self, x: float, z: float) -> float:
        n = self._sample_noise(x, z)
        basin = -8.0 if (abs(x) < 35 and abs(z) < 35) else 0
        ridge = max(0, (abs(x) + abs(z) - 430) / 8.0)
        return n * self.settings.terrain_height + basin + ridge

    def get_surface_normal(self, x: float, z: float) -> Vec3:
        e = 0.8
        h_l = self.get_height(x - e, z)
        h_r = self.get_height(x + e, z)
        h_d = self.get_height(x, z - e)
        h_u = self.get_height(x, z + e)
        normal = Vec3(h_l - h_r, 2.0 * e, h_d - h_u).normalized()
        return normal

    def clamp_to_world(self, pos: Vec3) -> Vec3:
        half = self.settings.world_size * 0.5
        pos.x = max(-half, min(half, pos.x))
        pos.z = max(-half, min(half, pos.z))
        pos.y = self.get_height(pos.x, pos.z)
        return pos

    def _build_terrain_entity(self) -> Entity:
        step = self.settings.terrain_step
        size = self.settings.world_size
        half = size // 2
        vertices = []
        triangles = []
        uvs = []
        width = size // step + 1

        for zi, z in enumerate(range(-half, half + 1, step)):
            for xi, x in enumerate(range(-half, half + 1, step)):
                y = self.get_height(x, z)
                vertices.append((x, y, z))
                uvs.append((xi / max(1, width - 1), zi / max(1, width - 1)))

        for zi in range(width - 1):
            for xi in range(width - 1):
                i = zi * width + xi
                triangles.extend((i, i + width, i + 1, i + 1, i + width, i + width + 1))

        mesh = Mesh(vertices=vertices, triangles=triangles, uvs=uvs, mode="triangle")
        mesh.generate_normals(smooth=True)

        return Entity(
            model=mesh,
            color=color.rgb(96, 199, 96),
            collider="mesh",
            shader=None,
        )
