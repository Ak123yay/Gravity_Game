# Gravity Control - Quick Start Guide

## Installation & Running (30 seconds)

```bash
# 1. Activate virtual environment
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate     # On Windows

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Run the game!
python game/main.py
```

## Controls

- **Arrow Keys**: Change gravity direction
- **R**: Restart level
- **ESC**: Pause/Resume
- **SPACE**: Next level (after completing)

## Objective

Navigate your auto-walking character to the blue exit by rotating gravity!

## Project Status

✅ **Implemented Features:**
- Gravity rotation system (4 cardinal directions)
- Auto-walking player character
- Physics engine (gravity, velocity, collision)
- Tilemap system with multiple tile types
- 3 sample levels with progressive difficulty
- HUD with timer and gravity indicator
- Pause menu and level complete screen
- Death and respawn system
- Hazard tiles (spikes)
- Unit and integration tests

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=game tests/
```

## File Structure

```
game/
├── __init__.py        # Package initialization
├── main.py            # Main game loop and entry point
├── physics.py         # Gravity manager and physics constants
├── player.py          # Player controller with auto-walk
├── level_manager.py   # Level loading and tilemap
└── ui.py              # HUD and menu screens

levels/
├── level_01.json      # Tutorial level
├── level_02.json      # Vertical tunnel challenge
└── level_03.json      # Spike hazards

tests/
├── test_physics.py         # Physics system tests
├── test_level_manager.py   # Tilemap tests
└── test_integration.py     # Integration tests
```

## Next Steps for Enhancement

1. **Audio System**: Add sound effects and music
2. **Better Graphics**: Replace colored rectangles with sprites
3. **More Levels**: Create 10-20 levels with increasing complexity
4. **Moving Platforms**: Add kinematic platform objects
5. **Push Blocks**: Interactive puzzle elements
6. **Particle Effects**: Visual polish for landings, deaths
7. **Level Editor**: In-game level creation tool

## Physics Constants (Tunable)

From `game/physics.py`:
- `G_STRENGTH = 900` px/s² - Gravity acceleration
- `MAX_FALL_SPEED = 1000` px/s - Terminal velocity

From `game/player.py`:
- `WALK_SPEED = 80` px/s - Auto-walk speed
- `PLAYER_WIDTH = 28` px - Player size
- `PLAYER_HEIGHT = 28` px

From `game/level_manager.py`:
- `TILE_SIZE = 32` px - Grid size

## Design Document

The full game design document is in the issue/PR description, containing:
- Complete mechanics description
- Physics formulas and math
- Level design philosophy
- Milestone breakdown
- 20+ pages of implementation details

---

**Ready to play?** Run `python game/main.py` and start controlling gravity! 🎮
