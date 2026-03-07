# AAA Cartoon Open-World Snake Game (Python / Ursina)

A modular 3D open-world snake survival prototype with:

- Procedural terrain (Perlin noise fallback)
- Terrain-aware snake locomotion
- AI snakes with personality-driven decision weights
- Ability system (dash, magnet, shield, shockwave)
- Combat + death-to-food loop
- Cartoon HUD and game-over menu
- Lightweight particle/VFX system with particle cap

## Run

```bash
pip install ursina noise numpy
python main.py
```

## Controls

- Move: snake auto-runs forward; steer with mouse projection (fallback A/D)
- Abilities: `1` Dash, `2` Magnet, `3` Shield, `4` Shockwave

## Project Layout

See `game/` subpackages:

- `world/`: terrain generation + procedural props
- `snake/`: player/AI snakes + segment logic
- `systems/`: food, abilities, AI, combat
- `effects/`: particles and visual effect wrappers
- `camera/`: smooth follow camera
- `ui/`: HUD + menu overlays
- `core/`: settings and game state
