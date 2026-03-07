from __future__ import annotations

from ursina import Entity, Button, Text, camera, application, color


class MenuController:
    def __init__(self, state) -> None:
        self.state = state
        self.root = Entity(parent=camera.ui)

        self.pause_panel = Entity(parent=self.root, model="quad", color=color.rgba(15, 15, 25, 180), scale=(0.5, 0.5), enabled=False)
        self.pause_label = Text(parent=self.pause_panel, text="Paused", scale=2, y=0.15)
        Button(parent=self.pause_panel, text="Quit", y=-0.12, scale=(0.22, 0.08), on_click=application.quit)

        self.game_over_panel = Entity(parent=self.root, model="quad", color=color.rgba(40, 10, 10, 190), scale=(0.55, 0.5), enabled=False)
        self.game_over_label = Text(parent=self.game_over_panel, text="Game Over", scale=2, y=0.14)
        self.score_text = Text(parent=self.game_over_panel, text="", y=0.02)
        Button(parent=self.game_over_panel, text="Quit", y=-0.14, scale=(0.22, 0.08), on_click=application.quit)

    def show_game_over(self, score: int) -> None:
        self.game_over_panel.enabled = True
        self.score_text.text = f"Final score: {score}"
