from __future__ import annotations

from ursina import Entity, color, Vec3


class SnakeSegment(Entity):
    def __init__(self, position: Vec3, tint=color.lime, scale=0.9) -> None:
        super().__init__(model="sphere", color=tint, position=position, scale=scale)

    def follow(self, target: Vec3, smoothing: float, dt: float) -> None:
        alpha = min(1.0, smoothing * dt)
        self.position = self.position.lerp(target, alpha)
