"""Physics and gravity management for Gravity Control game."""

import pygame
from pygame.math import Vector2


# Physics constants from design document
G_STRENGTH = 900  # px/s^2
MAX_FALL_SPEED = 1000  # px/s
PHYSICS_TICK = 60  # Hz


class GravityManager:
    """Manages the global gravity vector and rotation."""
    
    def __init__(self, g_strength=G_STRENGTH):
        """Initialize the gravity manager.
        
        Args:
            g_strength: Magnitude of gravity acceleration (px/s^2)
        """
        self.g_strength = g_strength
        self.g_vector = Vector2(0, g_strength)  # Start with gravity pointing down
        self.direction = 'down'
    
    def set_direction(self, direction):
        """Set gravity to one of four cardinal directions.
        
        Args:
            direction: One of 'down', 'up', 'left', 'right'
        """
        if direction == 'down':
            self.g_vector = Vector2(0, self.g_strength)
        elif direction == 'up':
            self.g_vector = Vector2(0, -self.g_strength)
        elif direction == 'left':
            self.g_vector = Vector2(-self.g_strength, 0)
        elif direction == 'right':
            self.g_vector = Vector2(self.g_strength, 0)
        
        self.direction = direction
    
    def apply(self, velocity, dt):
        """Apply gravity to a velocity vector.
        
        Args:
            velocity: Current velocity vector (px/s)
            dt: Delta time in seconds
            
        Returns:
            Updated velocity vector
        """
        return velocity + self.g_vector * dt
    
    def get_down_direction(self):
        """Get the current 'down' direction as a normalized vector.
        
        Returns:
            Normalized Vector2 pointing in the gravity direction
        """
        if self.g_vector.length() > 0:
            return self.g_vector.normalize()
        return Vector2(0, 1)
