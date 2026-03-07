from __future__ import annotations

from ursina import Vec3

from game.core.settings import Settings


class CombatSystem:
    def __init__(self, settings: Settings, state, food_system, effects) -> None:
        self.settings = settings
        self.state = state
        self.food_system = food_system
        self.effects = effects

    def update(self, player, ai_snakes) -> None:
        if player.is_dead:
            return
        self._player_vs_ai_bodies(player, ai_snakes)
        self._ai_vs_bodies(player, ai_snakes)

    def _player_vs_ai_bodies(self, player, ai_snakes) -> None:
        if player.is_shielded:
            return
        for ai in ai_snakes:
            if ai.is_dead:
                continue
            for seg in ai.segments[1:]:
                if self._distance(player.head.position, seg.position) < 1.05:
                    player.is_dead = True
                    self.effects.spawn_snake_death(player.head.position, player.head.color)
                    return

    def _ai_vs_bodies(self, player, ai_snakes) -> None:
        for ai in ai_snakes:
            if ai.is_dead:
                continue

            for seg in player.segments[1:]:
                if self._distance(ai.head.position, seg.position) < 0.95:
                    self._kill_ai(ai)
                    self.state.add_score(50)
                    break

            if ai.is_dead:
                continue

            for other in ai_snakes:
                if other is ai or other.is_dead:
                    continue
                for seg in other.segments[1:]:
                    if self._distance(ai.head.position, seg.position) < 0.95:
                        self._kill_ai(ai)
                        break
                if ai.is_dead:
                    break

    def _kill_ai(self, ai) -> None:
        ai.is_dead = True
        self.effects.spawn_snake_death(ai.head.position, ai.head.color)
        self.food_system.convert_segments_to_food(ai.segments)
        ai.head.disable()
        for seg in ai.segments:
            seg.disable()

    @staticmethod
    def _distance(a: Vec3, b: Vec3) -> float:
        return (a - b).length()
