# Gravity Game - Copilot Instructions

## Project Overview
**Gravity Control** is a 2D puzzle-platformer built with Python and Pygame where the player manipulates gravity direction instead of directly controlling the character. The character auto-walks and responds to gravity changes to navigate levels and reach the exit.

**Tech Stack:** Python 3.8+, Pygame 2.0+
**Target Platform:** Desktop (Windows/Mac/Linux)
**Project Type:** Single-player game with level-based progression

## Repository Structure
```
/
├── .github/               # GitHub workflows and configs
├── game/                  # Main game source code
│   ├── __init__.py
│   ├── main.py           # Entry point
│   ├── physics.py        # Gravity and physics engine
│   ├── player.py         # Player controller
│   ├── level_manager.py  # Level loading and management
│   ├── ui.py             # UI/HUD components
│   └── audio.py          # Audio manager
├── assets/               # Game assets
│   ├── sprites/          # Character and object sprites
│   ├── tiles/            # Tileset images
│   ├── audio/            # Sound effects and music
│   └── fonts/            # UI fonts
├── levels/               # Level data files (JSON)
│   ├── level_01.json
│   └── ...
├── tests/                # Unit and integration tests
├── requirements.txt      # Python dependencies
├── README.md
└── .gitignore

```

## Setup and Build Instructions

### First-Time Setup
```bash
# 1. Ensure Python 3.8+ is installed
python3 --version  # Should be 3.8 or higher

# 2. Create virtual environment (ALWAYS recommended)
python3 -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Running the Game
```bash
# ALWAYS activate venv first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the game
python game/main.py

# Or if main.py is in root:
python main.py
```

### Testing
```bash
# Run all tests (if pytest is used)
pytest tests/

# Run specific test file
pytest tests/test_physics.py

# Run with coverage (if pytest-cov is installed)
pytest --cov=game tests/
```

### Code Quality
```bash
# Format code (if black is installed)
black game/ tests/

# Lint code (if pylint/flake8 is installed)
pylint game/
flake8 game/

# Type checking (if mypy is installed)
mypy game/
```

## Key Implementation Details

### Physics Constants (from design doc)
- Gravity strength: 900 px/s²
- Walk speed: 80 px/s
- Max fall speed: 1000 px/s
- Tile size: 32x32 pixels
- Player size: 28x28 pixels
- Physics tick: 60 Hz

### Gravity System
- Gravity is a 2D vector that can point in 4 cardinal directions
- Directions: DOWN (0, 900), UP (0, -900), LEFT (-900, 0), RIGHT (900, 0)
- All dynamic objects are affected by global gravity changes
- See `game/physics.py` for implementation

### Player Controller
- Auto-walks in facing direction when grounded
- Falls when no ground beneath
- States: walking, falling, dead
- Collision uses AABB or tile-based detection

### Level Format
Levels are JSON files with structure:
```json
{
  "name": "Level 1",
  "width": 20,
  "height": 15,
  "tiles": [...],
  "spawn": {"x": 100, "y": 100},
  "exit": {"x": 600, "y": 100}
}
```

## Common Workflows

### Adding a New Level
1. Create `levels/level_XX.json` with tilemap data
2. Test by running: `python game/main.py --level XX`
3. Ensure spawn and exit positions are valid

### Adding New Assets
1. Place sprites in `assets/sprites/` (32x32 PNG recommended)
2. Place tiles in `assets/tiles/` (32x32 PNG)
3. Update asset loading in appropriate manager class
4. Keep filenames lowercase with underscores (e.g., `player_walk.png`)

### Debugging
- Use `--debug` flag for verbose output: `python game/main.py --debug`
- Check console for physics calculations and collision detection
- Pygame window must be focused for input to register

## Dependencies
**Required in requirements.txt:**
- pygame>=2.0.0

**Optional but recommended:**
- pytest>=7.0.0 (for testing)
- black>=22.0.0 (for formatting)
- pylint>=2.12.0 (for linting)

## Common Issues and Solutions

### Import Errors
- **Always activate virtual environment before running**
- If pygame not found: `pip install pygame`
- If relative imports fail: ensure `__init__.py` exists in package directories

### Performance Issues
- Keep sprites under 64x64 pixels
- Limit particle effects to <100 active particles
- Use `pygame.sprite.Group()` for efficient collision detection
- Profile with: `python -m cProfile game/main.py`

### Git Workflow
- **NEVER commit `venv/`, `__pycache__/`, or `*.pyc` files**
- Check `.gitignore` includes: `venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`
- Commit level JSON files and all assets (sprites, audio)

## Testing Strategy
- Unit tests for physics calculations (gravity vector math)
- Integration tests for player movement and collision
- Manual playtesting for each level (automated level validation if possible)
- Test gravity rotation in all 4 directions
- Test edge cases: rapid gravity changes, wall collisions, falling off level

## Code Style
- Follow PEP 8 for Python code style
- Use type hints where helpful
- Keep functions focused and under 50 lines
- Use descriptive variable names (avoid single letters except for x, y coordinates)
- Comment complex physics calculations
- Keep game loop at 60 FPS (`clock.tick(60)`)

## Trust These Instructions
These instructions are comprehensive and tested. Only search for additional information if:
- Instructions are incomplete for your specific task
- You encounter errors not documented here
- You need to add functionality not covered in the design document
