"""Level management and tilemap system for Gravity Control game."""

import json
import pygame
from pathlib import Path


# Tile constants
TILE_SIZE = 32  # px


class TileType:
    """Tile type constants."""
    EMPTY = '.'
    SOLID = '#'
    SPAWN = 'S'
    EXIT = 'E'
    SPIKE = '^'
    BUTTON = 'B'


class Tilemap:
    """Manages the game tilemap and collision detection."""
    
    def __init__(self, width=20, height=15, name=""):
        """Initialize the tilemap.
        
        Args:
            width: Width in tiles
            height: Height in tiles
            name: Level display name
        """
        self.width = width
        self.height = height
        self.name = name
        self.tile_size = TILE_SIZE
        self.tiles = [[TileType.EMPTY for _ in range(width)] for _ in range(height)]
        self.spawn_pos = (100, 100)
        self.exit_pos = (600, 100)
    
    def set_tile_size(self, new_size):
        """Set the tile size for rendering.

        Args:
            new_size: New tile size in pixels
        """
        old_size = self.tile_size
        self.tile_size = new_size

        # Rescale spawn and exit positions
        if old_size > 0:
            scale_factor = new_size / old_size
            self.spawn_pos = (int(self.spawn_pos[0] * scale_factor),
                             int(self.spawn_pos[1] * scale_factor))
            self.exit_pos = (int(self.exit_pos[0] * scale_factor),
                            int(self.exit_pos[1] * scale_factor))

    def set_tile(self, x, y, tile_type):
        """Set a tile at grid coordinates.

        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            tile_type: Tile type character
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_type
    
    def get_tile(self, x, y):
        """Get tile at grid coordinates.
        
        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            
        Returns:
            Tile type character or EMPTY if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return TileType.EMPTY
    
    def is_solid(self, pixel_x, pixel_y):
        """Check if a pixel position contains a solid tile.
        
        Args:
            pixel_x: X position in pixels
            pixel_y: Y position in pixels
            
        Returns:
            True if the position is solid, False otherwise
        """
        grid_x = pixel_x // self.tile_size
        grid_y = pixel_y // self.tile_size
        
        tile = self.get_tile(grid_x, grid_y)
        return tile == TileType.SOLID
    
    def is_hazard(self, pixel_x, pixel_y):
        """Check if a pixel position contains a hazard.
        
        Args:
            pixel_x: X position in pixels
            pixel_y: Y position in pixels
            
        Returns:
            True if the position is a hazard, False otherwise
        """
        grid_x = pixel_x // self.tile_size
        grid_y = pixel_y // self.tile_size
        
        tile = self.get_tile(grid_x, grid_y)
        return tile == TileType.SPIKE
    
    def is_exit(self, pixel_x, pixel_y, player_rect):
        """Check if player has reached the exit.

        Args:
            pixel_x: X position in pixels
            pixel_y: Y position in pixels
            player_rect: Player's collision rectangle

        Returns:
            True if player is at the exit
        """
        # Scale exit rect based on tile_size instead of hardcoded 32x32
        half_tile = self.tile_size // 2
        exit_rect = pygame.Rect(self.exit_pos[0] - half_tile, self.exit_pos[1] - half_tile,
                                self.tile_size, self.tile_size)
        return player_rect.colliderect(exit_rect)
    
    def from_ascii(self, ascii_map):
        """Load tilemap from ASCII art representation.
        
        Args:
            ascii_map: List of strings representing the level
        """
        self.height = len(ascii_map)
        self.width = max(len(row) for row in ascii_map) if ascii_map else 0
        self.tiles = []
        
        for y, row in enumerate(ascii_map):
            tile_row = []
            for x, char in enumerate(row):
                tile_row.append(char)
                
                # Set spawn and exit positions
                if char == TileType.SPAWN:
                    self.spawn_pos = (x * self.tile_size + self.tile_size // 2, 
                                     y * self.tile_size + self.tile_size // 2)
                elif char == TileType.EXIT:
                    self.exit_pos = (x * self.tile_size + self.tile_size // 2,
                                    y * self.tile_size + self.tile_size // 2)
            
            # Pad row to width
            while len(tile_row) < self.width:
                tile_row.append(TileType.EMPTY)
            
            self.tiles.append(tile_row)
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Draw the tilemap with enhanced visuals.

        Args:
            screen: Pygame surface to draw on
            camera_offset: Camera offset (x, y)
        """
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]

                if tile == TileType.EMPTY:
                    continue

                pixel_x = x * self.tile_size - camera_offset[0]
                pixel_y = y * self.tile_size - camera_offset[1]

                # Enhanced colors with better contrast and depth
                if tile == TileType.SOLID:
                    # Main color
                    color = (70, 75, 95)  # Darker blue-gray
                    highlight = (95, 105, 130)  # Lighter shade
                    shadow = (45, 50, 70)  # Darker shade
                    border = (55, 60, 80)  # Border color
                elif tile == TileType.SPIKE:
                    # Vibrant red with danger feel
                    color = (255, 70, 90)  # Vibrant red
                    highlight = (255, 120, 140)
                    shadow = (180, 40, 60)
                    border = (200, 50, 70)
                elif tile == TileType.SPAWN:
                    # Vibrant green
                    color = (80, 230, 150)  # Bright green
                    highlight = (120, 255, 180)
                    shadow = (50, 180, 110)
                    border = (60, 200, 130)
                elif tile == TileType.EXIT:
                    # Vibrant blue
                    color = (80, 180, 255)  # Bright blue
                    highlight = (120, 220, 255)
                    shadow = (50, 130, 200)
                    border = (60, 150, 220)
                else:
                    color = (120, 125, 145)  # Light gray
                    highlight = (150, 155, 175)
                    shadow = (90, 95, 115)
                    border = (100, 105, 125)

                # Draw shadow for depth
                shadow_rect = pygame.Rect(pixel_x + 2, pixel_y + 2, self.tile_size, self.tile_size)
                shadow_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                shadow_surface.fill((10, 10, 20, 80))
                screen.blit(shadow_surface, shadow_rect.topleft)

                # Draw main tile
                main_rect = pygame.Rect(pixel_x, pixel_y, self.tile_size, self.tile_size)
                pygame.draw.rect(screen, color, main_rect, border_radius=2)

                # Draw highlight for 3D effect (top-left)
                highlight_rect = pygame.Rect(pixel_x + 2, pixel_y + 2, self.tile_size - 4, self.tile_size // 2)
                pygame.draw.rect(screen, highlight, highlight_rect, border_radius=1)

                # Draw shadow for 3D effect (bottom-right inner)
                shadow_line_start_x = pixel_x + 2
                shadow_line_start_y = pixel_y + self.tile_size - 3
                shadow_line_end_x = pixel_x + self.tile_size - 2
                shadow_line_end_y = pixel_y + self.tile_size - 3
                pygame.draw.line(screen, shadow,
                               (shadow_line_start_x, shadow_line_start_y),
                               (shadow_line_end_x, shadow_line_end_y), 2)

                # Draw border
                pygame.draw.rect(screen, border, main_rect, 1, border_radius=2)

                # Special rendering for spikes
                if tile == TileType.SPIKE:
                    # Draw spike triangles pointing up
                    num_spikes = 3
                    spike_width = self.tile_size // num_spikes
                    for i in range(num_spikes):
                        spike_x = pixel_x + i * spike_width
                        points = [
                            (spike_x + spike_width // 2, pixel_y + 4),  # Top point
                            (spike_x, pixel_y + self.tile_size - 2),    # Bottom left
                            (spike_x + spike_width, pixel_y + self.tile_size - 2)  # Bottom right
                        ]
                        pygame.draw.polygon(screen, (255, 50, 70), points)
                        pygame.draw.polygon(screen, (200, 40, 60), points, 1)

                # Special rendering for exit (glowing effect)
                if tile == TileType.EXIT:
                    # Draw glowing center
                    center = (pixel_x + self.tile_size // 2, pixel_y + self.tile_size // 2)
                    pygame.draw.circle(screen, (150, 230, 255), center, self.tile_size // 4)
                    pygame.draw.circle(screen, (80, 180, 255), center, self.tile_size // 4, 2)

class LevelManager:
    """Manages level loading and progression."""
    
    def __init__(self, levels_dir="levels"):
        """Initialize the level manager.
        
        Args:
            levels_dir: Directory containing level files
        """
        self.levels_dir = Path(levels_dir)
        self.current_level = None
        self.level_number = 1
    
    def load_level(self, level_number):
        """Load a level from file.
        
        Args:
            level_number: Level number to load
            
        Returns:
            Tilemap instance or None if level doesn't exist
        """
        level_file = self.levels_dir / f"level_{level_number:02d}.json"
        
        # If JSON file doesn't exist, try to load a default level
        if not level_file.exists():
            return self._create_default_level(level_number)
        
        try:
            with open(level_file, 'r') as f:
                level_data = json.load(f)
            
            tilemap = Tilemap(level_data.get('width', 20), level_data.get('height', 15),
                              level_data.get('name', f"Level {level_number}"))
            
            # Load tiles from ASCII map if provided
            if 'map' in level_data:
                tilemap.from_ascii(level_data['map'])
            
            return tilemap
        except json.JSONDecodeError as e:
            print(f"Error loading level {level_number}: Invalid JSON format - {e}")
            print(f"Please verify the JSON syntax in {level_file}")
            return self._create_default_level(level_number)
        except Exception as e:
            print(f"Error loading level {level_number}: {e}")
            print(f"Please verify the file exists and is readable: {level_file}")
            return self._create_default_level(level_number)
    
    def _create_default_level(self, level_number):
        """Create a simple default level.
        
        Args:
            level_number: Level number
            
        Returns:
            Tilemap instance
        """
        # Create a simple test level
        if level_number == 1:
            ascii_map = [
                "###########",
                "#.........#",
                "#...S.....#",
                "#.........#",
                "#.....E...#",
                "###########"
            ]
        else:
            # Generic level
            ascii_map = [
                "##############",
                "#S...........E#",
                "#.............#",
                "##############"
            ]
        
        tilemap = Tilemap(name=f"Level {level_number}")
        tilemap.from_ascii(ascii_map)
        return tilemap
    
    def next_level(self):
        """Advance to the next level.
        
        Returns:
            New level number
        """
        self.level_number += 1
        return self.level_number
    
    def reset_level(self):
        """Reset to the current level."""
        return self.level_number
