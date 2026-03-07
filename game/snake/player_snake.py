from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ursina import Entity, Vec3, color, held_keys, mouse

from game.core.settings import Settings
from game.snake.snake_segment import SnakeSegment

if TYPE_CHECKING:
    from game.core.game_state import GameState
    from game.world.terrain import TerrainSystem
    from game.effects.visual_effects import VisualEffects


class PlayerSnake:
    def __init__(self, settings: Settings, terrain: "TerrainSystem", state: "GameState", effects: "VisualEffects") -> None:
        self.settings = settings
        self.terrain = terrain
        self.state = state
        self.effects = effects

        start = Vec3(0, terrain.get_height(0, 0), 0)
        self.head = Entity(model="sphere", color=color.azure, position=start, scale=1.2)
        self.direction = Vec3(0, 0, 1)
        self.energy = settings.base_energy
        self.speed_multiplier = 1.0
        self.is_shielded = False
        self.is_dead = False

        self.segments: list[SnakeSegment] = []
        for i in range(settings.initial_segments):
            seg_pos = start - self.direction * (i + 1) * settings.segment_spacing
            seg_pos.y = terrain.get_height(seg_pos.x, seg_pos.z)
            self.segments.append(SnakeSegment(seg_pos, tint=color.lime, scale=max(0.4, 0.95 - i * 0.03)))

    @property
    def speed(self) -> float:
        return (self.settings.player_base_speed + len(self.segments) * 0.18) * self.speed_multiplier

    def add_segment(self) -> None:
        tail = self.segments[-1].position if self.segments else self.head.position - self.direction
        new_seg = SnakeSegment(tail, tint=color.lime, scale=0.45)
        self.segments.append(new_seg)

    def remove_tail_segment(self) -> None:
        if not self.segments:
            self.is_dead = True
            return
        seg = self.segments.pop()
        seg.disable()

    def apply_energy(self, amount: float) -> None:
        self.energy = max(0, min(self.settings.base_energy, self.energy + amount))

    def update(self, dt: float) -> None:
        if self.is_dead:
            return

        self.energy -= self.settings.energy_drain_per_second * dt
        if self.energy <= 0:
            self.remove_tail_segment()
            self.speed_multiplier = 0.65
        else:
            self.speed_multiplier = 1.0

        self._turn_from_mouse(dt)
        self.head.position += self.direction * self.speed * dt
        self.head.position = self.terrain.clamp_to_world(self.head.position)

        normal = self.terrain.get_surface_normal(self.head.x, self.head.z)
        self.head.rotation = self.direction.normalized()
        self.head.up = normal

        anchor = self.head.position
        back = -self.direction.normalized()
        for i, seg in enumerate(self.segments):
            target = anchor + back * ((i + 1) * self.settings.segment_spacing)
            target.y = self.terrain.get_height(target.x, target.z)
            seg.follow(target, self.settings.segment_smoothing, dt)
            seg.up = self.terrain.get_surface_normal(seg.x, seg.z)

    def _turn_from_mouse(self, dt: float) -> None:
        if not mouse.world_point:
            horizontal = (held_keys["d"] - held_keys["a"]) * self.settings.turn_speed_rad
        else:
            to_mouse = mouse.world_point - self.head.position
            to_mouse.y = 0
            if to_mouse.length() < 0.001:
                return
            target_yaw = math.atan2(to_mouse.x, to_mouse.z)
            current_yaw = math.atan2(self.direction.x, self.direction.z)
            delta = (target_yaw - current_yaw + math.pi) % (2 * math.pi) - math.pi
            max_turn = self.settings.turn_speed_rad * (dt * 60)
            horizontal = max(-max_turn, min(max_turn, delta))

        c, s = math.cos(horizontal), math.sin(horizontal)
        x, z = self.direction.x, self.direction.z
        self.direction = Vec3(x * c + z * s, 0, z * c - x * s).normalized()
