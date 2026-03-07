from __future__ import annotations

import random
from dataclasses import dataclass

from ursina import held_keys

from game.core.settings import Settings


@dataclass
class AbilityState:
    cooldown_left: float = 0.0
    duration_left: float = 0.0
    charges: int = 1


class AbilitySystem:
    def __init__(self, settings: Settings, player, effects) -> None:
        self.settings = settings
        self.player = player
        self.effects = effects
        self.abilities = {name: AbilityState(charges=1) for name in settings.ability_cooldowns}
        self.keybinds = {"1": "dash", "2": "magnet", "3": "shield", "4": "shockwave"}

    def update(self, dt: float) -> None:
        for key, name in self.keybinds.items():
            if held_keys[key]:
                self.trigger(name)

        for name, data in self.abilities.items():
            data.cooldown_left = max(0.0, data.cooldown_left - dt)
            if data.duration_left > 0:
                data.duration_left = max(0.0, data.duration_left - dt)
                self._apply_ability_effect(name, active=True)
            else:
                self._apply_ability_effect(name, active=False)

    def trigger(self, name: str) -> bool:
        data = self.abilities[name]
        if data.cooldown_left > 0 or data.charges <= 0:
            return False
        data.duration_left = self.settings.ability_durations[name]
        data.cooldown_left = self.settings.ability_cooldowns[name]
        data.charges -= 1
        self.effects.spawn_ability_fx(self.player.head.position, name)
        return True

    def is_active(self, name: str) -> bool:
        return self.abilities[name].duration_left > 0

    def grant_random_charge(self) -> None:
        choice = random.choice(list(self.abilities.keys()))
        self.abilities[choice].charges += 1

    def _apply_ability_effect(self, name: str, active: bool) -> None:
        if name == "dash":
            self.player.speed_multiplier = 1.75 if active else 1.0
        elif name == "shield":
            self.player.is_shielded = active
