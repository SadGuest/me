from __future__ import annotations

import random

from ursina import Vec3, color

from game.core.settings import Settings
from game.snake.ai_snake import AISnake, AIPersonality


PERSONALITIES = [
    AIPersonality("Aggressive", 0.55, 0.35, 0.10),
    AIPersonality("Food Hunter", 0.8, 0.1, 0.1),
    AIPersonality("Defensive", 0.65, 0.1, 0.25),
    AIPersonality("Explorer", 0.55, 0.15, 0.3),
]


class AISystem:
    def __init__(self, settings: Settings, terrain, food_system, state, effects) -> None:
        self.settings = settings
        self.terrain = terrain
        self.food_system = food_system
        self.state = state
        self.effects = effects
        self.ai_snakes: list[AISnake] = []
        self._remaining_to_spawn = settings.target_ai_count
        self._palette = [color.red, color.orange, color.violet, color.cyan, color.magenta, color.yellow, color.azure]

    def begin_spawning(self) -> None:
        self._remaining_to_spawn = self.settings.target_ai_count

    def spawn_batch(self, batch_size: int) -> bool:
        count = min(batch_size, self._remaining_to_spawn)
        for _ in range(count):
            self._spawn_one()
        self._remaining_to_spawn -= count
        return self._remaining_to_spawn <= 0

    def _spawn_one(self) -> None:
        half = self.settings.world_size * 0.45
        x, z = random.uniform(-half, half), random.uniform(-half, half)
        spawn = Vec3(x, self.terrain.get_height(x, z), z)
        personality = random.choice(PERSONALITIES)
        tint = self._palette[len(self.ai_snakes) % len(self._palette)]
        self.ai_snakes.append(AISnake(self.settings, self.terrain, spawn, tint, personality))

    def update(self, dt: float, player) -> None:
        for ai in self.ai_snakes:
            if ai.is_dead:
                continue
            self._decide_target(ai, player)
            ai.update(dt)

    def _decide_target(self, ai: AISnake, player) -> None:
        roll = random.random()
        food_cutoff = ai.personality.food_bias
        attack_cutoff = food_cutoff + ai.personality.attack_bias

        if roll <= food_cutoff and self.food_system.food:
            target_food = min(self.food_system.food, key=lambda f: (f.position - ai.head.position).length())
            ai.set_target(target_food.position)
            return

        if roll <= attack_cutoff:
            if len(player.segments) < ai.size:
                ai.set_target(player.head.position)
                return
            ai.set_target(ai.head.position - (player.head.position - ai.head.position).normalized() * 8)
            return

        offset = Vec3(random.uniform(-20, 20), 0, random.uniform(-20, 20))
        ai.set_target(self.terrain.clamp_to_world(ai.head.position + offset))
