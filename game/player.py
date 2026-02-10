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
        self._clamp_velocity(gravity_manager)
        
        # Check ground detection
        self._check_ground(tilemap, gravity_manager)
        
        # Auto-walk if grounded
        if self.is_grounded:
            self._auto_walk(gravity_manager)
        
        # Move X axis
        delta_x = self.vel.x * dt
        self.pos.x += delta_x
        self.rect.x = int(self.pos.x)
        self._resolve_axis(tilemap, gravity_manager, "x", delta_x)
        
        # Move Y axis
        delta_y = self.vel.y * dt
        self.pos.y += delta_y
        self.rect.y = int(self.pos.y)
        self._resolve_axis(tilemap, gravity_manager, "y", delta_y)
        
        # Re-check ground after resolving collisions
        self._check_ground(tilemap, gravity_manager)
        
    def _clamp_velocity(self, gravity_manager):
        """Clamp velocity along the gravity axis to max fall speed."""
        gravity_dir = gravity_manager.get_down_direction()
        if abs(gravity_dir.y) >= abs(gravity_dir.x):
            self.vel.y = max(min(self.vel.y, MAX_FALL_SPEED), -MAX_FALL_SPEED)
        else:
            self.vel.x = max(min(self.vel.x, MAX_FALL_SPEED), -MAX_FALL_SPEED)

    def _get_solid_tile_rects(self, tilemap):
        """Return solid tile rects overlapped by the player."""
        tile_size = tilemap.tile_size
        left = max(self.rect.left // tile_size, 0)
        right = min((self.rect.right - 1) // tile_size, tilemap.width - 1)
        top = max(self.rect.top // tile_size, 0)
        bottom = min((self.rect.bottom - 1) // tile_size, tilemap.height - 1)
        
        if right < left or bottom < top:
            return []
        
        rects = []
        for tile_y in range(top, bottom + 1):
            for tile_x in range(left, right + 1):
                if tilemap.is_solid(tile_x * tile_size + 1, tile_y * tile_size + 1):
                    rects.append(pygame.Rect(tile_x * tile_size, tile_y * tile_size, tile_size, tile_size))
        return rects

    def _is_walk_axis(self, gravity_manager, axis):
        """Return True if the walk axis matches the given axis."""
        gravity_dir = gravity_manager.get_down_direction()
        if abs(gravity_dir.y) >= abs(gravity_dir.x):
            return axis == "x"
        return axis == "y"

    def _resolve_axis(self, tilemap, gravity_manager, axis, delta):
        """Resolve collisions along a single axis."""
        if delta == 0:
            return
        
        collisions = [rect for rect in self._get_solid_tile_rects(tilemap) if self.rect.colliderect(rect)]
        if not collisions:
            return
        
        if axis == "x":
            if delta > 0:
                target = min(rect.left for rect in collisions)
                self.rect.right = target
            else:
                target = max(rect.right for rect in collisions)
                self.rect.left = target
            self.pos.x = self.rect.x
            self.vel.x = 0
            if self.is_grounded and self._is_walk_axis(gravity_manager, "x"):
                self.facing_right = not self.facing_right
        else:
            if delta > 0:
                target = min(rect.top for rect in collisions)
                self.rect.bottom = target
            else:
                target = max(rect.bottom for rect in collisions)
                self.rect.top = target
            self.pos.y = self.rect.y
            self.vel.y = 0
            if self.is_grounded and self._is_walk_axis(gravity_manager, "y"):
                self.facing_right = not self.facing_right

    def _check_ground(self, tilemap, gravity_manager):
        """Check if player is on the ground relative to current gravity.
        
        Args:
            tilemap: Current level's tilemap
            gravity_manager: GravityManager instance
        """
        gravity_dir = gravity_manager.get_down_direction()
        probe_offset = 2
        
        if abs(gravity_dir.y) >= abs(gravity_dir.x):
            # Gravity is vertical, probe below/above
            x_positions = [self.rect.left + 2, self.rect.centerx, self.rect.right - 2]
            if gravity_dir.y > 0:
                check_y = self.rect.bottom + probe_offset
            else:
                check_y = self.rect.top - probe_offset
            
            self.is_grounded = any(tilemap.is_solid(int(x), int(check_y)) for x in x_positions)
        else:
            # Gravity is horizontal, probe left/right
            y_positions = [self.rect.top + 2, self.rect.centery, self.rect.bottom - 2]
            if gravity_dir.x > 0:
                check_x = self.rect.right + probe_offset
            else:
                check_x = self.rect.left - probe_offset
            
            self.is_grounded = any(tilemap.is_solid(int(check_x), int(y)) for y in y_positions)
    
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
        """Deprecated: collision handling is now split into axis-specific methods."""
        pass
    
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
