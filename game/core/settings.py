from dataclasses import dataclass, field


@dataclass
class Settings:
    world_size: int = 600
    terrain_scale: float = 0.02
    terrain_height: float = 40.0
    terrain_step: int = 4

    max_particles: int = 200
    target_ai_count: int = 8

    player_base_speed: float = 18.0
    ai_base_speed: float = 14.0
    turn_speed_rad: float = 0.05

    base_energy: float = 100.0
    energy_drain_per_second: float = 2.4
    food_common_energy: float = 12.0
    food_rare_energy: float = 28.0

    segment_spacing: float = 1.2
    segment_smoothing: float = 8.0
    initial_segments: int = 10

    food_target_count: int = 240

    camera_position_lerp: float = 0.03
    camera_look_lerp: float = 0.05

    ability_cooldowns: dict = field(
        default_factory=lambda: {
            "dash": 7.0,
            "magnet": 14.0,
            "shield": 18.0,
            "shockwave": 12.0,
        }
    )

    ability_durations: dict = field(
        default_factory=lambda: {
            "dash": 1.2,
            "magnet": 4.0,
            "shield": 5.0,
            "shockwave": 0.6,
        }
    )
