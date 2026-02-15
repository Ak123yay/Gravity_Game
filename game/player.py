"""Player controller for Gravity Control game."""

import pygame
from pygame.math import Vector2
from game.physics import MAX_FALL_SPEED


# Player constants from design document
WALK_SPEED = 80  # px/s
PLAYER_WIDTH = 28  # px
PLAYER_HEIGHT = 28  # px
GROUND_FRICTION = 0.85  # Applied to velocity when grounded (lower = more friction)


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

        # Apply friction to gravity axis when grounded to prevent sliding
        if self.is_grounded:
            gravity_dir = gravity_manager.get_down_direction()
            if abs(gravity_dir.y) >= abs(gravity_dir.x):
                # Vertical gravity - apply friction to Y velocity
                self.vel.y *= GROUND_FRICTION
            else:
                # Horizontal gravity - apply friction to X velocity
                self.vel.x *= GROUND_FRICTION

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
        """Resolve collisions along a single axis with improved accuracy.

        Args:
            tilemap: Current level's tilemap
            gravity_manager: GravityManager instance
            axis: "x" or "y"
            delta: Movement delta for this frame
        """
        if delta == 0:
            return

        collisions = [rect for rect in self._get_solid_tile_rects(tilemap) if self.rect.colliderect(rect)]
        if not collisions:
            return

        if axis == "x":
            if delta > 0:
                # Moving right, align to leftmost collision
                target = min(rect.left for rect in collisions)
                self.rect.right = target
            else:
                # Moving left, align to rightmost collision
                target = max(rect.right for rect in collisions)
                self.rect.left = target
            # Update position and stop velocity
            self.pos.x = float(self.rect.x)
            self.vel.x = 0
            # Reverse direction if grounded and walking along this axis
            if self.is_grounded and self._is_walk_axis(gravity_manager, "x"):
                self.facing_right = not self.facing_right
        else:  # axis == "y"
            if delta > 0:
                # Moving down, align to topmost collision
                target = min(rect.top for rect in collisions)
                self.rect.bottom = target
            else:
                # Moving up, align to bottommost collision
                target = max(rect.bottom for rect in collisions)
                self.rect.top = target
            # Update position and stop velocity
            self.pos.y = float(self.rect.y)
            self.vel.y = 0
            # Reverse direction if grounded and walking along this axis
            if self.is_grounded and self._is_walk_axis(gravity_manager, "y"):
                self.facing_right = not self.facing_right

    def _check_ground(self, tilemap, gravity_manager):
        """Check if player is on the ground relative to current gravity.

        Args:
            tilemap: Current level's tilemap
            gravity_manager: GravityManager instance
        """
        gravity_dir = gravity_manager.get_down_direction()
        probe_offset = 4  # Increased from 2 for more reliable detection

        if abs(gravity_dir.y) >= abs(gravity_dir.x):
            # Gravity is vertical, probe below/above with more points
            x_positions = [
                self.rect.left + 2,
                self.rect.left + self.width // 4,
                self.rect.centerx,
                self.rect.right - self.width // 4,
                self.rect.right - 2
            ]
            if gravity_dir.y > 0:
                check_y = self.rect.bottom + probe_offset
            else:
                check_y = self.rect.top - probe_offset

            self.is_grounded = any(tilemap.is_solid(int(x), int(check_y)) for x in x_positions)
        else:
            # Gravity is horizontal, probe left/right with more points
            y_positions = [
                self.rect.top + 2,
                self.rect.top + self.height // 4,
                self.rect.centery,
                self.rect.bottom - self.height // 4,
                self.rect.bottom - 2
            ]
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
        """Draw the player with enhanced visuals.

        Args:
            screen: Pygame surface to draw on
            camera_offset: Camera offset (x, y)
        """
        if not self.alive:
            return

        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]

        # Modern color scheme for player
        main_color = (100, 220, 255)  # Bright cyan
        outline_color = (50, 120, 180)  # Darker cyan
        face_color = (255, 200, 80)  # Warm orange for facing indicator

        # Draw shadow/glow effect
        shadow_rect = pygame.Rect(draw_x + 2, draw_y + 2, self.width, self.height)
        shadow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        shadow_surface.fill((10, 10, 30, 100))
        screen.blit(shadow_surface, shadow_rect.topleft)

        # Draw player outline (for depth)
        outline_rect = pygame.Rect(draw_x - 1, draw_y - 1, self.width + 2, self.height + 2)
        pygame.draw.rect(screen, outline_color, outline_rect, border_radius=3)

        # Draw player main body
        player_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
        pygame.draw.rect(screen, main_color, player_rect, border_radius=3)

        # Draw inner highlight for 3D effect
        highlight_rect = pygame.Rect(draw_x + 2, draw_y + 2, self.width - 4, self.height // 2)
        pygame.draw.rect(screen, (150, 240, 255), highlight_rect, border_radius=2)

        # Draw facing direction indicator (larger and more visible)
        indicator_size = 6
        if self.facing_right:
            indicator_x = draw_x + self.width - indicator_size - 3
        else:
            indicator_x = draw_x + 3

        indicator_y = draw_y + self.height // 2 - indicator_size // 2
        # Draw indicator with outline
        pygame.draw.circle(screen, (100, 50, 20), (indicator_x + indicator_size // 2 + 1, indicator_y + indicator_size // 2 + 1), indicator_size // 2 + 1)
        pygame.draw.circle(screen, face_color, (indicator_x + indicator_size // 2, indicator_y + indicator_size // 2), indicator_size // 2)
