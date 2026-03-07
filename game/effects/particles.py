from __future__ import annotations

from dataclasses import dataclass

from ursina import Entity, Text, Vec3, color


@dataclass
class Particle:
    entity: Entity
    velocity: Vec3
    life: float


class ParticleSystem:
    def __init__(self, max_particles: int = 200) -> None:
        self.max_particles = max_particles
        self.active: list[Particle] = []

    def emit(self, position: Vec3, tint=color.white, velocity=Vec3(0, 2, 0), life: float = 1.2, text: str | None = None) -> None:
        if len(self.active) >= self.max_particles:
            oldest = self.active.pop(0)
            oldest.entity.disable()

        ent = Text(text=text, position=position, color=tint, scale=1.5) if text else Entity(model="sphere", color=tint, scale=0.25, position=position)
        self.active.append(Particle(ent, velocity, life))

    def update(self, dt: float) -> None:
        dead = []
        for p in self.active:
            p.life -= dt
            p.entity.position += p.velocity * dt
            p.entity.alpha = max(0, p.life)
            if p.life <= 0:
                dead.append(p)
        for p in dead:
            p.entity.disable()
            self.active.remove(p)
