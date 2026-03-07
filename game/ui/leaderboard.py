from dataclasses import dataclass, field


@dataclass
class Leaderboard:
    scores: list[tuple[str, int]] = field(default_factory=list)

    def submit(self, name: str, score: int) -> None:
        self.scores.append((name, score))
        self.scores.sort(key=lambda item: item[1], reverse=True)
        self.scores = self.scores[:10]
