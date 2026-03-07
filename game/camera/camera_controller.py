from __future__ import annotations

from ursina import camera, Vec3

from game.core.settings import Settings


class FollowCameraController:
    def __init__(self, settings: Settings, player) -> None:
        self.settings = settings
        self.player = player
        camera.fov = 75

    def update(self, dt: float) -> None:
        del dt
        backward = -self.player.direction.normalized()
        dynamic_dist = 18 + len(self.player.segments) * 0.25
        desired = self.player.head.position + backward * dynamic_dist + Vec3(0, 9, 0)
        look_target = self.player.head.position + self.player.direction * 7

        camera.position = camera.position.lerp(desired, self.settings.camera_position_lerp)
        camera.look_at(camera.world_position.lerp(look_target, self.settings.camera_look_lerp))

        turn_tilt = self.player.direction.x * -3
        camera.rotation_z = camera.rotation_z * 0.9 + turn_tilt * 0.1
