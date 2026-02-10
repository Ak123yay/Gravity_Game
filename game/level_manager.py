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
    
    def __init__(self, width=20, height=15):
        """Initialize the tilemap.
        
        Args:
            width: Width in tiles
            height: Height in tiles
        """
        self.width = width
        self.height = height
        self.tile_size = TILE_SIZE
        self.tiles = [[TileType.EMPTY for _ in range(width)] for _ in range(height)]
        self.spawn_pos = (100, 100)
        self.exit_pos = (600, 100)
    
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
        exit_rect = pygame.Rect(self.exit_pos[0] - 16, self.exit_pos[1] - 16, 32, 32)
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
        """Draw the tilemap.
        
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
                
                # Choose color based on tile type
                if tile == TileType.SOLID:
                    color = (100, 100, 100)  # Gray
                elif tile == TileType.SPIKE:
                    color = (255, 0, 0)  # Red
                elif tile == TileType.SPAWN:
                    color = (0, 255, 0)  # Green
                elif tile == TileType.EXIT:
                    color = (0, 100, 255)  # Blue
                else:
                    color = (150, 150, 150)  # Light gray
                
                pygame.draw.rect(screen, color, 
                               (pixel_x, pixel_y, self.tile_size, self.tile_size))
                
                # Draw border for clarity
                pygame.draw.rect(screen, (50, 50, 50), 
                               (pixel_x, pixel_y, self.tile_size, self.tile_size), 1)


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
            
            tilemap = Tilemap(level_data.get('width', 20), level_data.get('height', 15))
            
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
        
        tilemap = Tilemap()
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
