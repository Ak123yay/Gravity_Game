"""Unit tests for tilemap and level management."""

import pytest
from game.level_manager import Tilemap, TileType


class TestTilemap:
    """Test the Tilemap class."""
    
    def test_initialization(self):
        """Test tilemap initializes with correct defaults."""
        tm = Tilemap(20, 15)
        assert tm.width == 20
        assert tm.height == 15
        assert tm.tile_size == 32
        assert len(tm.tiles) == 15
        assert len(tm.tiles[0]) == 20
    
    def test_set_and_get_tile(self):
        """Test setting and getting tiles."""
        tm = Tilemap(10, 10)
        tm.set_tile(5, 5, TileType.SOLID)
        assert tm.get_tile(5, 5) == TileType.SOLID
    
    def test_get_tile_out_of_bounds(self):
        """Test getting tile outside map bounds."""
        tm = Tilemap(10, 10)
        assert tm.get_tile(-1, 0) == TileType.EMPTY
        assert tm.get_tile(100, 100) == TileType.EMPTY
    
    def test_is_solid(self):
        """Test solid tile detection."""
        tm = Tilemap(10, 10)
        tm.set_tile(5, 5, TileType.SOLID)
        
        # Position in pixels (5 * 32 = 160)
        assert tm.is_solid(160, 160) is True
        assert tm.is_solid(0, 0) is False
    
    def test_is_hazard(self):
        """Test hazard tile detection."""
        tm = Tilemap(10, 10)
        tm.set_tile(3, 3, TileType.SPIKE)
        
        # Position in pixels (3 * 32 = 96)
        assert tm.is_hazard(96, 96) is True
        assert tm.is_hazard(0, 0) is False
    
    def test_from_ascii(self):
        """Test loading tilemap from ASCII."""
        ascii_map = [
            "######",
            "#S..E#",
            "######"
        ]
        
        tm = Tilemap()
        tm.from_ascii(ascii_map)
        
        assert tm.width == 6
        assert tm.height == 3
        assert tm.get_tile(0, 0) == TileType.SOLID
        assert tm.get_tile(1, 1) == TileType.SPAWN
        assert tm.get_tile(4, 1) == TileType.EXIT
    
    def test_ascii_sets_spawn_position(self):
        """Test that ASCII loading sets spawn position."""
        ascii_map = [
            "######",
            "#S...#",
            "######"
        ]
        
        tm = Tilemap()
        tm.from_ascii(ascii_map)
        
        # Spawn at grid (1, 1) should be pixel (1*32+16, 1*32+16) = (48, 48)
        assert tm.spawn_pos == (48, 48)
    
    def test_ascii_sets_exit_position(self):
        """Test that ASCII loading sets exit position."""
        ascii_map = [
            "######",
            "#...E#",
            "######"
        ]
        
        tm = Tilemap()
        tm.from_ascii(ascii_map)
        
        # Exit at grid (4, 1) should be pixel (4*32+16, 1*32+16) = (144, 48)
        assert tm.exit_pos == (144, 48)
    
    def test_ascii_with_multiple_tile_types(self):
        """Test ASCII map with various tile types."""
        ascii_map = [
            "########",
            "#S..^..#",
            "#....E.#",
            "########"
        ]
        
        tm = Tilemap()
        tm.from_ascii(ascii_map)
        
        assert tm.get_tile(0, 0) == TileType.SOLID
        assert tm.get_tile(1, 1) == TileType.SPAWN
        assert tm.get_tile(4, 1) == TileType.SPIKE
        assert tm.get_tile(5, 2) == TileType.EXIT
        assert tm.get_tile(2, 1) == TileType.EMPTY
