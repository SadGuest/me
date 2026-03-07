from __future__ import annotations

import math
import random
from dataclasses import dataclass

from ursina import Entity, Vec3, color, time

from game.core.settings import Settings
from game.world.terrain import TerrainSystem


@dataclass
class FoodSpec:
    kind: str
    energy: float
    score: int
    tint: object


FOOD_TABLE = {
    "common": FoodSpec("common", 12, 10, color.rgb(255, 170, 60)),
    "rare": FoodSpec("rare", 28, 25, color.rgb(150, 80, 255)),
    "golden": FoodSpec("golden", 15, 35, color.rgb(255, 230, 80)),
    "ability": FoodSpec("ability", 5, 20, color.rgb(70, 255, 220)),
}


class FoodPickup(Entity):
    def __init__(self, position: Vec3, spec: FoodSpec) -> None:
        super().__init__(model="sphere", color=spec.tint, position=position, scale=0.6)
        self.spec = spec
        self.base_y = position.y
        self.seed = random.uniform(0, 1000)

    def tick(self) -> None:
        self.rotation_y += 70 * time.dt
        self.y = self.base_y + 0.25 * (1 + math.sin(time.time() * 3.5 + self.seed))


class FoodSystem:
    def __init__(self, settings: Settings, terrain: TerrainSystem, effects) -> None:
        self.settings = settings
        self.terrain = terrain
        self.effects = effects
        self.food: list[FoodPickup] = []
        self._food_to_spawn = settings.food_target_count

    def begin_spawning(self) -> None:
        self._food_to_spawn = self.settings.food_target_count

    def spawn_batch(self, batch_size: int) -> bool:
        count = min(batch_size, self._food_to_spawn)
        for _ in range(count):
            self._spawn_food()
        self._food_to_spawn -= count
        return self._food_to_spawn <= 0

    def _roll_kind(self) -> str:
        r = random.random()
        if r < 0.72:
            return "common"
        if r < 0.9:
            return "rare"
        if r < 0.97:
            return "golden"
        return "ability"

    def _spawn_food(self, kind: str | None = None, position: Vec3 | None = None) -> None:
        half = self.settings.world_size * 0.48
        kind = kind or self._roll_kind()
        if position is None:
            x = random.uniform(-half, half)
            z = random.uniform(-half, half)
            y = self.terrain.get_height(x, z) + 0.8
            position = Vec3(x, y, z)
        self.food.append(FoodPickup(position, FOOD_TABLE[kind]))

    def convert_segments_to_food(self, segments: list[Entity]) -> None:
        for seg in segments:
            self._spawn_food("common", seg.position + Vec3(0, 0.4, 0))

    def update(self, dt: float, player, ai_snakes, ability_system) -> None:
        del dt
        for f in self.food:
            f.tick()

        magnet_active = ability_system.is_active("magnet")
        eaten: list[FoodPickup] = []

        for f in self.food:
            if magnet_active:
                pull = player.head.position - f.position
                if pull.length() < 16:
                    f.position += pull.normalized() * 20 * time.dt
                    f.y = self.terrain.get_height(f.x, f.z) + 0.8

            if distance(f.position, player.head.position) < 1.6:
                self._apply_to_player(f, player, ability_system)
                eaten.append(f)
                continue

            for ai in ai_snakes:
                if ai.is_dead:
                    continue
                if distance(f.position, ai.head.position) < 1.4:
                    ai.segments.append(ai.segments[-1])
                    eaten.append(f)
                    break

        for f in eaten:
            if f in self.food:
                self.food.remove(f)
                f.disable()
                self._spawn_food()

    def _apply_to_player(self, f: FoodPickup, player, ability_system) -> None:
        player.apply_energy(f.spec.energy)
        player.state.add_score(f.spec.score)
        if f.spec.kind in {"common", "rare"}:
            player.add_segment()
        elif f.spec.kind == "golden":
            ability_system.trigger("dash")
        elif f.spec.kind == "ability":
            ability_system.grant_random_charge()
        self.effects.spawn_pickup_burst(f.position, f.spec.tint, f"+{f.spec.score}")


def distance(a: Vec3, b: Vec3) -> float:
    d = a - b
    return d.length()
