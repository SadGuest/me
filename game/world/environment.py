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
        self._spawn_queue: list[tuple[str, object, object, bool]] = []

    def begin_population(self) -> None:
        self._spawn_queue.clear()
        self._queue_scatter("cube", 110, color.rgb(61, 136, 51), (0.5, 4, 0.5), True)
        self._queue_scatter("sphere", 140, color.rgb(92, 182, 88), 0.7, False)
        self._queue_scatter("cube", 90, color.rgb(115, 115, 115), (1.2, 1.0, 1.1), True)
        self._queue_scatter("quad", 120, color.rgb(255, 148, 215), 0.45, False)

    def populate_batch(self, batch_size: int) -> bool:
        for _ in range(min(batch_size, len(self._spawn_queue))):
            model, tint, scale, casts_shadow = self._spawn_queue.pop()
            self._spawn_object(model, tint, scale, casts_shadow)
        return not self._spawn_queue

    def _queue_scatter(self, model: str, count: int, tint, scale, casts_shadow: bool) -> None:
        for _ in range(count):
            self._spawn_queue.append((model, tint, scale, casts_shadow))

    def _spawn_object(self, model: str, tint, scale, casts_shadow: bool) -> None:
        half = self.settings.world_size * 0.48
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
            cast_shadows=casts_shadow,
        )
        self.objects.append(obj)
