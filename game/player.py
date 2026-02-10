"""Player controller for Gravity Control game."""

import pygame
from pygame.math import Vector2
from game.physics import MAX_FALL_SPEED


# Player constants from design document
WALK_SPEED = 80  # px/s
PLAYER_WIDTH = 28  # px
PLAYER_HEIGHT = 28  # px


class Player:
    """Auto-walking player character controlled by gravity."""
    
    def __init__(self, x, y):
        """Initialize the player.
        
        Args:
            x: Starting x position
            y: Starting y position
        """
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        
        # State tracking
        self.is_grounded = False
        self.facing_right = True
        self.alive = True
        
        # Auto-walk speed
        self.walk_speed = WALK_SPEED
    
    def update(self, dt, gravity_manager, tilemap):
        """Update player physics and position.
        
        Args:
            dt: Delta time in seconds
            gravity_manager: GravityManager instance
            tilemap: Current level's tilemap
        """
        if not self.alive:
            return
        
        # Apply gravity to velocity
        self.vel = gravity_manager.apply(self.vel, dt)
        
        # Clamp velocity to max fall speed
        if self.vel.length() > MAX_FALL_SPEED:
            self.vel.scale_to_length(MAX_FALL_SPEED)
        
        # Check ground detection
        self._check_ground(tilemap, gravity_manager)
        
        # Auto-walk if grounded
        if self.is_grounded:
            self._auto_walk(gravity_manager)
        
        # Apply velocity to position
        self.pos += self.vel * dt
        
        # Update collision rect
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        
        # Handle collisions
        self._handle_collisions(tilemap, gravity_manager)
    
    def _check_ground(self, tilemap, gravity_manager):
        """Check if player is on the ground relative to current gravity.
        
        Args:
            tilemap: Current level's tilemap
            gravity_manager: GravityManager instance
        """
        # Get the gravity direction
        gravity_dir = gravity_manager.get_down_direction()
        
        # Check for ground in the direction of gravity
        # For now, simple ground check - will be enhanced with tilemap collision
        check_distance = 5  # pixels to check below player
        
        check_pos = self.pos + gravity_dir * (max(self.width, self.height) / 2 + check_distance)
        
        # Check if there's a solid tile at the check position
        self.is_grounded = tilemap.is_solid(int(check_pos.x), int(check_pos.y))
    
    def _auto_walk(self, gravity_manager):
        """Make player auto-walk along the ground.
        
        Args:
            gravity_manager: GravityManager instance
        """
        # Determine walk direction perpendicular to gravity
        gravity_dir = gravity_manager.get_down_direction()
        
        # Walk direction depends on current gravity orientation
        if abs(gravity_dir.y) > abs(gravity_dir.x):
            # Gravity is vertical, walk horizontally
            walk_dir = Vector2(1 if self.facing_right else -1, 0)
        else:
            # Gravity is horizontal, walk vertically
            walk_dir = Vector2(0, 1 if self.facing_right else -1)
        
        # Set walk velocity (overrides other velocity in walk direction)
        if abs(gravity_dir.y) > abs(gravity_dir.x):
            self.vel.x = walk_dir.x * self.walk_speed
            # Keep vertical velocity from gravity
        else:
            self.vel.y = walk_dir.y * self.walk_speed
            # Keep horizontal velocity from gravity
    
    def _handle_collisions(self, tilemap, gravity_manager):
        """Handle collisions with tilemap.
        
        Args:
            tilemap: Current level's tilemap
            gravity_manager: GravityManager instance
        """
        # Simple collision detection with tiles
        # Check all corners of the player's bounding box
        corners = [
            (self.rect.left, self.rect.top),
            (self.rect.right, self.rect.top),
            (self.rect.left, self.rect.bottom),
            (self.rect.right, self.rect.bottom)
        ]
        
        for corner_x, corner_y in corners:
            if tilemap.is_solid(corner_x, corner_y):
                # Player hit a wall, reverse direction
                self.facing_right = not self.facing_right
                break
    
    def kill(self):
        """Kill the player."""
        self.alive = False
        self.vel = Vector2(0, 0)
    
    def reset(self, x, y):
        """Reset player to starting position.
        
        Args:
            x: Reset x position
            y: Reset y position
        """
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.alive = True
        self.facing_right = True
        self.is_grounded = False
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Draw the player.
        
        Args:
            screen: Pygame surface to draw on
            camera_offset: Camera offset (x, y)
        """
        if not self.alive:
            return
        
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        # Draw player as a simple colored rectangle for now
        color = (200, 200, 100)  # Yellow-ish
        pygame.draw.rect(screen, color, (draw_x, draw_y, self.width, self.height))
        
        # Draw a small indicator showing facing direction
        indicator_size = 4
        if self.facing_right:
            indicator_x = draw_x + self.width - indicator_size
        else:
            indicator_x = draw_x
        pygame.draw.rect(screen, (255, 0, 0), 
                        (indicator_x, draw_y + self.height // 2, indicator_size, indicator_size))
