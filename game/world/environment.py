from __future__ import annotations

import random

from ursina import Entity, color

from game.core.settings import Settings
from game.world.terrain import TerrainSystem


class EnvironmentSystem:
    def __init__(self, settings: Settings, terrain: TerrainSystem) -> None:
        self.settings = settings
        self.terrain = terrain
        self.objects: list[Entity] = []

    def populate_world(self) -> None:
        self._scatter("cube", 180, color.rgb(61, 136, 51), (0.5, 4, 0.5))
        self._scatter("sphere", 220, color.rgb(92, 182, 88), 0.7)
        self._scatter("cube", 120, color.rgb(115, 115, 115), (1.2, 1.0, 1.1))
        self._scatter("quad", 260, color.rgb(255, 148, 215), 0.45)

    def _scatter(self, model: str, count: int, tint, scale) -> None:
        half = self.settings.world_size * 0.48
        for _ in range(count):
            x = random.uniform(-half, half)
            z = random.uniform(-half, half)
            y = self.terrain.get_height(x, z)
            obj = Entity(
                model=model,
                color=tint,
                x=x,
                y=y,
                z=z,
                scale=scale,
                rotation_y=random.uniform(0, 360),
                cast_shadows=True,
            )
            self.objects.append(obj)
