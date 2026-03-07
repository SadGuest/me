from dataclasses import dataclass


@dataclass
class GameState:
    is_playing: bool = True
    is_paused: bool = False
    is_game_over: bool = False
    score: int = 0

    def add_score(self, amount: int) -> None:
        self.score += amount

    def toggle_pause(self) -> None:
        self.is_paused = not self.is_paused
        self.is_playing = not self.is_paused and not self.is_game_over

    def trigger_game_over(self) -> None:
        self.is_game_over = True
        self.is_playing = False
