from __future__ import annotations

from ursina import Entity, Text, color, camera

from game.core.settings import Settings


class HUD:
    def __init__(self, settings: Settings, state, player, ability_system) -> None:
        self.settings = settings
        self.state = state
        self.player = player
        self.ability_system = ability_system

        self.root = Entity(parent=camera.ui)
        self.energy_back = Entity(parent=self.root, model="quad", color=color.rgba(0, 0, 0, 140), scale=(0.42, 0.04), position=(-0.56, 0.45))
        self.energy_fill = Entity(parent=self.energy_back, model="quad", color=color.rgb(80, 255, 120), scale=(0.98, 0.8), position=(-0.01, 0), origin=(-0.5, 0))

        self.score_label = Text(parent=self.root, text="Score: 0", position=(-0.87, 0.4), scale=1.2, color=color.white)
        self.mini_label = Text(parent=self.root, text="Minimap: N/A", position=(0.62, 0.42), scale=1.0, color=color.white)
        self.leaderboard = Text(parent=self.root, text="Leaderboard\n1. You", position=(0.58, 0.20), scale=0.9)
        self.abilities = Text(parent=self.root, text="", position=(-0.87, -0.43), scale=0.9)

    def update(self) -> None:
        energy_ratio = max(0, min(1, self.player.energy / self.settings.base_energy))
        self.energy_fill.scale_x = 0.98 * energy_ratio
        self.score_label.text = f"Score: {self.state.score}"

        lines = ["Abilities"]
        for name, info in self.ability_system.abilities.items():
            state = "READY" if info.cooldown_left <= 0 and info.charges > 0 else f"CD {info.cooldown_left:0.1f}s"
            if info.duration_left > 0:
                state = f"ACTIVE {info.duration_left:0.1f}s"
            lines.append(f"{name.title()} [{info.charges}] - {state}")
        self.abilities.text = "\n".join(lines)
