from __future__ import annotations

import math
import random
from dataclasses import dataclass

from ursina import Vec3, Entity, color

from game.core.settings import Settings
from game.snake.snake_segment import SnakeSegment
from game.world.terrain import TerrainSystem


@dataclass
class AIPersonality:
    name: str
    food_bias: float
    attack_bias: float
    wander_bias: float


class AISnake:
    def __init__(self, settings: Settings, terrain: TerrainSystem, spawn: Vec3, tint, personality: AIPersonality) -> None:
        self.settings = settings
        self.terrain = terrain
        self.personality = personality
        self.head = Entity(model="sphere", color=tint, position=spawn, scale=1.05)
        self.direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
        self.speed = settings.ai_base_speed * random.uniform(0.9, 1.15)
        self.segments = [SnakeSegment(spawn - self.direction * (i + 1), tint=tint, scale=0.7) for i in range(random.randint(6, 13))]
        self.target = spawn + self.direction * 10
        self.is_dead = False

    @property
    def size(self) -> int:
        return len(self.segments)

    def set_target(self, pos: Vec3) -> None:
        self.target = pos

    def update(self, dt: float) -> None:
        if self.is_dead:
            return
        to_target = self.target - self.head.position
        to_target.y = 0
        if to_target.length() > 0.2:
            desired = to_target.normalized()
            current_yaw = math.atan2(self.direction.x, self.direction.z)
            target_yaw = math.atan2(desired.x, desired.z)
            delta = (target_yaw - current_yaw + math.pi) % (2 * math.pi) - math.pi
            max_turn = self.settings.turn_speed_rad * 0.9 * (dt * 60)
            turn = max(-max_turn, min(max_turn, delta))
            c, s = math.cos(turn), math.sin(turn)
            x, z = self.direction.x, self.direction.z
            self.direction = Vec3(x * c + z * s, 0, z * c - x * s).normalized()

        self.head.position += self.direction * self.speed * dt
        self.head.position = self.terrain.clamp_to_world(self.head.position)

        back = -self.direction
        for i, seg in enumerate(self.segments):
            t = self.head.position + back * ((i + 1) * self.settings.segment_spacing)
            t.y = self.terrain.get_height(t.x, t.z)
            seg.follow(t, self.settings.segment_smoothing, dt)
