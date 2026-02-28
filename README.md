# Gravity Control

A 2D puzzle-platformer where you don't control the hero, you control gravity!

## Overview

**Gravity Control** is a unique puzzle game where the player character moves automatically, and your only control is rotating the world's gravity direction. Manipulate gravity to help your character walk, fall, and navigate through challenging levels to reach the exit.

## Features

- **Gravity Rotation**: Control gravity in four cardinal directions (up, down, left, right)
- **Auto-walking Character**: The player walks automatically; you guide them with gravity
- **Physics-based Gameplay**: Realistic gravity physics with proper acceleration and velocity
- **Multiple Levels**: Progressive difficulty with tutorial levels and challenging puzzles
- **Simple Controls**: Easy to learn, challenging to master

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Ak123yay/Gravity_Game.git
cd Gravity_Game
```

2. Create and activate a virtual environment (recommended):
```bash
# On Linux/Mac:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

### Running the Game

```bash
# Make sure your virtual environment is activated
python game/main.py
```

### Controls

- **Arrow Keys**: Rotate gravity direction
  - ⬆️ Up Arrow: Gravity points upward
  - ⬇️ Down Arrow: Gravity points downward
  - ⬅️ Left Arrow: Gravity points left
  - ➡️ Right Arrow: Gravity points right
- **R**: Restart current level
- **ESC**: Pause/Resume game
- **SPACE**: Continue to next level (after completing a level)

### Objective

- Navigate your character to the **blue exit** tile
- Avoid **red hazards** (spikes)
- Use gravity rotation to traverse walls and ceilings
- Complete levels as quickly as possible!

## Game Mechanics

### Gravity System
- Gravity applies a constant acceleration of 900 px/s² in the current direction
- Changing gravity affects all physics objects globally
- The character automatically walks at 80 px/s when grounded

### Character Behavior
- Auto-walks forward when on a surface
- Falls when no ground beneath
- Reverses direction when hitting walls
- Dies on contact with hazards or falling off the map

### Level Elements
- **Green tile (S)**: Spawn point
- **Blue tile (E)**: Exit/goal
- **Gray tiles (#)**: Solid platforms
- **Red spikes (^)**: Hazards that kill the player

## Level Design

The game includes multiple levels with progressive difficulty:

1. **Level 1**: Basic gravity introduction
2. **Level 2**: Vertical tunnels requiring gravity rotation
3. **Level 3**: Hazards and timing challenges

### Creating Custom Levels

Levels are stored as JSON files in the `levels/` directory. Format:

```json
{
  "name": "Level Name",
  "width": 15,
  "height": 10,
  "map": [
    "###############",
    "#S...........E#",
    "#.............#",
    "###############"
  ]
}
```

**Tile Legend:**
- `.` = Empty space
- `#` = Solid wall
- `S` = Player spawn
- `E` = Exit
- `^` = Spike hazard

## Development

### Project Structure

```
Gravity_Game/
├── game/                   # Main game source code
│   ├── __init__.py
│   ├── main.py            # Game entry point and main loop
│   ├── physics.py         # Gravity and physics engine
│   ├── player.py          # Player controller
│   ├── level_manager.py   # Level loading and tilemap
│   └── ui.py              # UI and HUD components
├── levels/                # Level JSON files
│   ├── level_01.json
│   ├── level_02.json
│   └── level_03.json
├── assets/                # Game assets (sprites, audio, etc.)
│   ├── sprites/
│   ├── tiles/
│   ├── audio/
│   └── fonts/
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
└── README.md
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=game tests/
```

### Code Quality

```bash
# Format code
black game/ tests/

# Lint code
pylint game/
flake8 game/
```

## Technical Details

### Physics Constants

- Gravity strength: 900 px/s²
- Walk speed: 80 px/s
- Max fall speed: 1000 px/s
- Tile size: 32×32 pixels
- Player size: 28×28 pixels
- Physics tick rate: 60 Hz

### Dependencies

- **pygame >= 2.0.0**: Game engine and graphics
- **pytest >= 7.0.0**: Testing framework (optional)
- **black >= 22.0.0**: Code formatter (optional)
- **pylint >= 2.12.0**: Code linter (optional)

## Credits

**Design & Development**: Based on the comprehensive game design document
**Engine**: Pygame
**Concept**: Gravity manipulation puzzle-platformer

## License

This project is open source. See LICENSE file for details.

## Troubleshooting

### Common Issues

**Import Errors / Module Not Found**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Game Window Not Opening**
- Ensure pygame is installed: `pip install pygame`
- Check that your system supports pygame (graphics drivers)

**Performance Issues**
- Game runs at 60 FPS by default
- Reduce screen resolution if needed
- Close other applications

### Getting Help

If you encounter issues:
1. Check that Python 3.8+ is installed: `python --version`
2. Verify pygame installation: `python -c "import pygame; print(pygame.ver)"`
3. Ensure virtual environment is activated
4. Check console output for error messages

## Future Enhancements

Potential features for future versions:
- Sound effects and background music
- Animated sprites
- Moving platforms
- Push blocks and interactive elements
- Level editor
- Speedrun timer and leaderboards
- More levels with increasing complexity

---

**Have fun controlling gravity!** 🎮
