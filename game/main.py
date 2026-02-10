"""Main game loop for Gravity Control."""

import pygame
from pygame.math import Vector2
import sys

from game.physics import GravityManager, PHYSICS_TICK
from game.player import Player
from game.level_manager import LevelManager
from game.ui import UI


# Screen constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60


class GameState:
    """Game state constants."""
    PLAYING = "playing"
    PAUSED = "paused"
    LEVEL_COMPLETE = "level_complete"
    DEAD = "dead"


class GravityGame:
    """Main game class for Gravity Control."""
    
    def __init__(self):
        """Initialize the game."""
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Gravity Control")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game systems
        self.gravity_manager = GravityManager()
        self.level_manager = LevelManager()
        self.ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Game state
        self.state = GameState.PLAYING
        self.timer = 0.0
        self.level_completion_time = 0.0
        
        # Load first level
        self.current_tilemap = self.level_manager.load_level(1)
        
        # Create player at spawn position
        spawn_x, spawn_y = self.current_tilemap.spawn_pos
        self.player = Player(spawn_x, spawn_y)
        
        print("Gravity Control - Game Started!")
        print("Use Arrow Keys to rotate gravity")
        print("Press R to restart, ESC to pause")
    
    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                # Pause toggle
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                
                # Restart level
                if event.key == pygame.K_r:
                    self.restart_level()
                
                # Gravity rotation (only when playing)
                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_DOWN:
                        self.gravity_manager.set_direction('down')
                        print("Gravity: DOWN")
                    elif event.key == pygame.K_UP:
                        self.gravity_manager.set_direction('up')
                        print("Gravity: UP")
                    elif event.key == pygame.K_LEFT:
                        self.gravity_manager.set_direction('left')
                        print("Gravity: LEFT")
                    elif event.key == pygame.K_RIGHT:
                        self.gravity_manager.set_direction('right')
                        print("Gravity: RIGHT")
                
                # Continue to next level after completion
                if self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_SPACE:
                        self.next_level()
    
    def update(self, dt):
        """Update game logic.
        
        Args:
            dt: Delta time in seconds
        """
        if self.state != GameState.PLAYING:
            return
        
        # Update timer
        self.timer += dt
        
        # Update player
        self.player.update(dt, self.gravity_manager, self.current_tilemap)
        
        # Check for hazards
        if self.current_tilemap.is_hazard(int(self.player.pos.x), int(self.player.pos.y)):
            self.player.kill()
            self.state = GameState.DEAD
            print("Player died on hazard!")
        
        # Check for exit
        if self.current_tilemap.is_exit(int(self.player.pos.x), int(self.player.pos.y), self.player.rect):
            self.level_completion_time = self.timer
            self.state = GameState.LEVEL_COMPLETE
            print(f"Level complete! Time: {self.timer:.2f}s")
        
        # Check if player fell off the map
        if (self.player.pos.x < -100 or self.player.pos.x > (self.current_tilemap.width * 32 + 100) or
            self.player.pos.y < -100 or self.player.pos.y > (self.current_tilemap.height * 32 + 100)):
            self.player.kill()
            self.state = GameState.DEAD
            print("Player fell off the map!")
    
    def draw(self):
        """Draw the game."""
        # Clear screen with dark background
        self.screen.fill((30, 30, 40))
        
        # Draw level
        self.current_tilemap.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        self.ui.draw_hud(self.screen, self.level_manager.level_number, 
                        self.timer, self.gravity_manager.direction)
        
        # Draw state-specific UI
        if self.state == GameState.PAUSED:
            self.ui.draw_pause_menu(self.screen)
        elif self.state == GameState.LEVEL_COMPLETE:
            self.ui.draw_level_complete(self.screen, self.level_completion_time)
        elif self.state == GameState.DEAD:
            self.ui.draw_death_screen(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def restart_level(self):
        """Restart the current level."""
        print(f"Restarting level {self.level_manager.level_number}")
        
        # Reset timer
        self.timer = 0.0
        
        # Reset gravity
        self.gravity_manager.set_direction('down')
        
        # Reset player
        spawn_x, spawn_y = self.current_tilemap.spawn_pos
        self.player.reset(spawn_x, spawn_y)
        
        # Reset state
        self.state = GameState.PLAYING
    
    def next_level(self):
        """Load the next level."""
        level_num = self.level_manager.next_level()
        print(f"Loading level {level_num}")
        
        # Load new level
        self.current_tilemap = self.level_manager.load_level(level_num)
        
        # Reset timer
        self.timer = 0.0
        
        # Reset gravity
        self.gravity_manager.set_direction('down')
        
        # Reset player at new spawn
        spawn_x, spawn_y = self.current_tilemap.spawn_pos
        self.player.reset(spawn_x, spawn_y)
        
        # Reset state
        self.state = GameState.PLAYING
    
    def run(self):
        """Main game loop."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            # Handle input
            self.handle_input()
            
            # Update game
            self.update(dt)
            
            # Draw game
            self.draw()
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the game."""
    game = GravityGame()
    game.run()


if __name__ == "__main__":
    main()
