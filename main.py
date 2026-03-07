from ursina import Ursina, Sky, color, time

from game.core.settings import Settings
from game.core.game_state import GameState
from game.world.terrain import TerrainSystem
from game.world.environment import EnvironmentSystem
from game.systems.food_system import FoodSystem
from game.effects.particles import ParticleSystem
from game.effects.visual_effects import VisualEffects
from game.snake.player_snake import PlayerSnake
from game.systems.ai_system import AISystem
from game.systems.ability_system import AbilitySystem
from game.systems.combat_system import CombatSystem
from game.camera.camera_controller import FollowCameraController
from game.ui.hud import HUD
from game.ui.menus import MenuController


class SnakeOpenWorldGame:
    def __init__(self) -> None:
        self.app = Ursina(borderless=False, title="AAA Cartoon Open-World Snake")
        self.settings = Settings()
        self.state = GameState()

        Sky(color=color.rgb(120, 220, 255))

        self.terrain = TerrainSystem(self.settings)
        self.environment = EnvironmentSystem(self.settings, self.terrain)
        self.environment.populate_world()

        self.particles = ParticleSystem(max_particles=self.settings.max_particles)
        self.effects = VisualEffects(self.particles)

        self.food_system = FoodSystem(self.settings, self.terrain, self.effects)
        self.food_system.spawn_initial_food()

        self.player = PlayerSnake(self.settings, self.terrain, self.state, self.effects)
        self.ai_system = AISystem(self.settings, self.terrain, self.food_system, self.state, self.effects)
        self.ai_system.spawn_ai_snakes()

        self.ability_system = AbilitySystem(self.settings, self.player, self.effects)
        self.combat_system = CombatSystem(self.settings, self.state, self.food_system, self.effects)

        self.camera = FollowCameraController(self.settings, self.player)
        self.hud = HUD(self.settings, self.state, self.player, self.ability_system)
        self.menus = MenuController(self.state)

        self.app.update = self.update

    def update(self) -> None:
        if not self.state.is_playing:
            return

        dt = time.dt
        self.player.update(dt)
        self.ai_system.update(dt, self.player)
        self.food_system.update(dt, self.player, self.ai_system.ai_snakes, self.ability_system)
        self.ability_system.update(dt)
        self.combat_system.update(self.player, self.ai_system.ai_snakes)
        self.camera.update(dt)
        self.hud.update()
        self.particles.update(dt)

        if self.player.is_dead:
            self.state.trigger_game_over()
            self.menus.show_game_over(self.state.score)

    def run(self) -> None:
        self.app.run()


if __name__ == "__main__":
    SnakeOpenWorldGame().run()
