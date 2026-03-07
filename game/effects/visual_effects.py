from __future__ import annotations

import random

from ursina import Vec3, color


class VisualEffects:
    def __init__(self, particles) -> None:
        self.particles = particles

    def spawn_pickup_burst(self, position: Vec3, tint, text: str) -> None:
        self.particles.emit(position + Vec3(0, 1.2, 0), tint=tint, text=text, velocity=Vec3(0, 1.4, 0), life=1.0)
        for _ in range(5):
            vel = Vec3(random.uniform(-1.3, 1.3), random.uniform(1.4, 3.1), random.uniform(-1.3, 1.3))
            self.particles.emit(position, tint=tint, velocity=vel, life=0.8)

    def spawn_snake_death(self, position: Vec3, tint) -> None:
        for _ in range(18):
            vel = Vec3(random.uniform(-3, 3), random.uniform(1, 4), random.uniform(-3, 3))
            self.particles.emit(position, tint=tint, velocity=vel, life=1.4)

    def spawn_ability_fx(self, position: Vec3, ability_name: str) -> None:
        map_color = {
            "dash": color.azure,
            "magnet": color.orange,
            "shield": color.cyan,
            "shockwave": color.violet,
        }
        tint = map_color.get(ability_name, color.white)
        for _ in range(10):
            self.particles.emit(position, tint=tint, velocity=Vec3(random.uniform(-2, 2), random.uniform(1, 2), random.uniform(-2, 2)), life=0.8)
