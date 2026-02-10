"""Integration test - verify game can initialize and run basic logic."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pygame
from game.physics import GravityManager
from game.player import Player
from game.level_manager import LevelManager

def test_game_initialization():
    """Test that game components can be initialized."""
    pygame.init()
    
    # Create game systems
    gravity_manager = GravityManager()
    level_manager = LevelManager()
    
    # Load a level
    tilemap = level_manager.load_level(1)
    
    # Create player
    spawn_x, spawn_y = tilemap.spawn_pos
    player = Player(spawn_x, spawn_y)
    
    print("✓ Game initialized successfully")
    print(f"  Gravity: {gravity_manager.direction}")
    print(f"  Level size: {tilemap.width}x{tilemap.height}")
    print(f"  Player spawn: ({spawn_x}, {spawn_y})")
    
    # Test gravity rotation
    gravity_manager.set_direction('up')
    assert gravity_manager.direction == 'up'
    print("✓ Gravity rotation works")
    
    # Test player update (one frame)
    dt = 1.0 / 60.0  # 60 FPS
    player.update(dt, gravity_manager, tilemap)
    print(f"✓ Player update works, position: ({player.pos.x:.1f}, {player.pos.y:.1f})")
    
    pygame.quit()
    print("✓ All integration tests passed!")

if __name__ == "__main__":
    test_game_initialization()
