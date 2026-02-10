"""Unit tests for physics and gravity system."""

import pytest
from pygame.math import Vector2
from game.physics import GravityManager, G_STRENGTH


class TestGravityManager:
    """Test the GravityManager class."""
    
    def test_initialization(self):
        """Test gravity manager initializes with correct defaults."""
        gm = GravityManager()
        assert gm.g_strength == G_STRENGTH
        assert gm.direction == 'down'
        assert gm.g_vector == Vector2(0, G_STRENGTH)
    
    def test_set_direction_down(self):
        """Test setting gravity to down direction."""
        gm = GravityManager()
        gm.set_direction('down')
        assert gm.g_vector == Vector2(0, G_STRENGTH)
        assert gm.direction == 'down'
    
    def test_set_direction_up(self):
        """Test setting gravity to up direction."""
        gm = GravityManager()
        gm.set_direction('up')
        assert gm.g_vector == Vector2(0, -G_STRENGTH)
        assert gm.direction == 'up'
    
    def test_set_direction_left(self):
        """Test setting gravity to left direction."""
        gm = GravityManager()
        gm.set_direction('left')
        assert gm.g_vector == Vector2(-G_STRENGTH, 0)
        assert gm.direction == 'left'
    
    def test_set_direction_right(self):
        """Test setting gravity to right direction."""
        gm = GravityManager()
        gm.set_direction('right')
        assert gm.g_vector == Vector2(G_STRENGTH, 0)
        assert gm.direction == 'right'
    
    def test_apply_gravity(self):
        """Test applying gravity to velocity."""
        gm = GravityManager()
        gm.set_direction('down')
        
        initial_vel = Vector2(0, 0)
        dt = 0.1  # 100ms
        
        new_vel = gm.apply(initial_vel, dt)
        
        # After 0.1s with 900 px/s^2, velocity should be 90 px/s
        expected = Vector2(0, 90)
        assert new_vel == expected
    
    def test_apply_gravity_horizontal(self):
        """Test applying horizontal gravity."""
        gm = GravityManager()
        gm.set_direction('right')
        
        initial_vel = Vector2(0, 0)
        dt = 0.05  # 50ms
        
        new_vel = gm.apply(initial_vel, dt)
        
        # After 0.05s with 900 px/s^2, velocity should be 45 px/s
        expected = Vector2(45, 0)
        assert new_vel == expected
    
    def test_get_down_direction(self):
        """Test getting normalized down direction."""
        gm = GravityManager()
        
        gm.set_direction('down')
        assert gm.get_down_direction() == Vector2(0, 1)
        
        gm.set_direction('up')
        assert gm.get_down_direction() == Vector2(0, -1)
        
        gm.set_direction('left')
        assert gm.get_down_direction() == Vector2(-1, 0)
        
        gm.set_direction('right')
        assert gm.get_down_direction() == Vector2(1, 0)
    
    def test_custom_gravity_strength(self):
        """Test creating gravity manager with custom strength."""
        custom_strength = 500
        gm = GravityManager(custom_strength)
        
        assert gm.g_strength == custom_strength
        assert gm.g_vector == Vector2(0, custom_strength)
