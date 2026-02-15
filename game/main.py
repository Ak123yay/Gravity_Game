"""Main game loop for Gravity Control."""

import sys
from pathlib import Path

import pygame
from pygame.math import Vector2

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from game.physics import GravityManager, PHYSICS_TICK
from game.player import Player
from game.level_manager import LevelManager, TILE_SIZE
from game.ui import UI
from game.settings import Settings, GameState as GameStateManager
from game.particles import ParticleManager
from game.effects import ScreenShake
from game.transitions import TransitionManager


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
    MENU = "menu"
    SETTINGS = "settings"


class GravityGame:
    """Main game class for Gravity Control."""
    
    def __init__(self):
        """Initialize the game."""
        pygame.init()

        # Set up windowed, resizable display so player can run in window mode
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.screen_width, self.screen_height = self.screen.get_size()
        pygame.display.set_caption("Gravity Control")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.accumulator = 0.0

        # Initialize settings and game state manager
        self.settings = Settings()
        self.game_state_manager = GameStateManager()

        # Initialize particle system
        particle_limit = self.settings.get_particle_limit()
        self.particle_manager = ParticleManager(particle_limit)

        # Initialize effects
        self.screen_shake = ScreenShake()
        self.screen_shake.set_enabled(self.settings.get("graphics", "screen_shake"))

        # Initialize transitions
        self.transition_manager = TransitionManager()

        # Initialize game systems
        self.gravity_manager = GravityManager()
        self.level_manager = LevelManager()
        self.ui = UI(self.screen_width, self.screen_height)

        # Game state
        self.state = GameState.MENU
        self.menu_option = 0
        self.timer = 0.0
        self.level_completion_time = 0.0
        self.death_count = 0

        # Load first level and scale to screen
        self.current_tilemap = self.level_manager.load_level(1)
        self._scale_current_level()

        print("Gravity Control - Game Started!")

    def _scale_current_level(self):
        """Scale current tilemap so it fills the window and create/update player size.

        This computes an integer tile size that fits the level into the current
        window and applies it to the tilemap. It also ensures the player exists
        with a size appropriate for the tile size and places the player at the
        level spawn.
        """
        if not self.current_tilemap:
            return

        # Compute tile size to make the level fill the screen
        tile_w = max(1, self.screen_width // max(1, self.current_tilemap.width))
        tile_h = max(1, self.screen_height // max(1, self.current_tilemap.height))
        tile_size = min(tile_w, tile_h)

        # Apply to tilemap
        self.current_tilemap.set_tile_size(tile_size)

        # Create or update player with a size relative to tile size
        spawn_x, spawn_y = self.current_tilemap.spawn_pos
        desired_player_size = max(8, int(tile_size * 0.4))

        if hasattr(self, 'player') and self.player is not None:
            # Update player size and reposition
            self.player.width = desired_player_size
            self.player.height = desired_player_size
            self.player.rect.width = self.player.width
            self.player.rect.height = self.player.height
            # Reset player to spawn
            self.player.reset(spawn_x, spawn_y)
        else:
            # Create new player at spawn
            self.player = Player(spawn_x, spawn_y)
            self.player.width = desired_player_size
            self.player.height = desired_player_size
            self.player.rect.width = self.player.width
            self.player.rect.height = self.player.height
    
    def handle_input(self):
        """Handle user input."""
        # Update mouse position for UI
        mouse_pos = pygame.mouse.get_pos()
        self.ui.update_mouse_pos(mouse_pos)

        for event in pygame.event.get():
            # Handle window resize to keep levels filling the screen
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.screen_width, self.screen_height = self.screen.get_size()
                # Update UI dimensions and rescale current level
                self.ui = UI(self.screen_width, self.screen_height)
                self._scale_current_level()
                continue
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                # Menu Navigation
                if self.state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        self.menu_option = (self.menu_option - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        self.menu_option = (self.menu_option + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if self.menu_option == 0:  # Start Game
                            self.ui.reset_menu_animation()
                            self.start_game()
                        elif self.menu_option == 1:  # Settings
                            self.state = GameState.SETTINGS
                            self.ui.settings_category = 0
                        elif self.menu_option == 2:  # Quit
                            self.running = False
                    return

                # Settings Menu Navigation
                if self.state == GameState.SETTINGS:
                    if event.key == pygame.K_UP:
                        self.ui.settings_category = (self.ui.settings_category - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        self.ui.settings_category = (self.ui.settings_category + 1) % 4
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        self.state = GameState.MENU
                        self.menu_option = 0
                    return

                # Pause toggle
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                        self.ui.reset_pause_animation()
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING

                # Quit from Pause Menu
                if self.state == GameState.PAUSED and event.key == pygame.K_q:
                    self.state = GameState.MENU

                # Restart level
                if event.key == pygame.K_r:
                    self.restart_level()

                # Gravity rotation (only when playing)
                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_DOWN:
                        self.gravity_manager.set_direction('down')
                    elif event.key == pygame.K_UP:
                        self.gravity_manager.set_direction('up')
                    elif event.key == pygame.K_LEFT:
                        self.gravity_manager.set_direction('left')
                    elif event.key == pygame.K_RIGHT:
                        self.gravity_manager.set_direction('right')

                # Continue to next level after completion
                if self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_SPACE:
                        self.next_level()

    def start_game(self):
        """Start a new game from Level 1."""
        self.level_manager.level_number = 1
        self.current_tilemap = self.level_manager.load_level(1)
        self.restart_level()
        self.state = GameState.PLAYING

    def update(self, dt):
        """Update game logic.

        Args:
            dt: Delta time in seconds
        """
        # Always update UI for animations
        self.ui.update(dt)

        # Update particle system
        self.particle_manager.update(dt)

        # Update screen shake
        self.screen_shake.update(dt)

        # Update transitions
        self.transition_manager.update(dt)

        if self.state == GameState.MENU or self.state == GameState.PAUSED:
            return

        if self.state == GameState.SETTINGS:
            return

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
            self.death_count += 1
            self.game_state_manager.increment_deaths()
            # Trigger death effects
            self.screen_shake.trigger(10, 0.25)
            self.particle_manager.emit('gameplay', 'burst',
                                      x=self.player.pos.x, y=self.player.pos.y,
                                      count=30, color=(255, 80, 100),
                                      speed_range=(80, 200), size_range=(3, 6))
            self.ui.reset_death_animation()
            print("Player died on hazard!")

        # Check for exit
        if self.current_tilemap.is_exit(int(self.player.pos.x), int(self.player.pos.y), self.player.rect):
            self.level_completion_time = self.timer
            self.state = GameState.LEVEL_COMPLETE
            # Trigger level complete effects
            self.screen_shake.trigger(6, 0.15)
            self.particle_manager.emit('ui', 'confetti',
                                      x=self.screen_width // 2, y=0,
                                      count=50, colors=[(80, 230, 150), (80, 180, 255), (255, 180, 70)])
            self.ui.reset_level_complete_animation()
            # Save best time
            is_new_best = self.game_state_manager.set_best_time(self.level_manager.level_number, self.timer)
            self.game_state_manager.mark_level_complete(self.level_manager.level_number)
            print(f"Level complete! Time: {self.timer:.2f}s" + (" (New Best!)" if is_new_best else ""))

        # Check if player fell off the map
        map_w_px = self.current_tilemap.width * self.current_tilemap.tile_size
        map_h_px = self.current_tilemap.height * self.current_tilemap.tile_size
        if (self.player.pos.x < -100 or self.player.pos.x > (map_w_px + 100) or
            self.player.pos.y < -100 or self.player.pos.y > (map_h_px + 100)):
            self.player.kill()
            self.state = GameState.DEAD
            self.death_count += 1
            self.game_state_manager.increment_deaths()
            self.screen_shake.trigger(10, 0.25)
            self.ui.reset_death_animation()
            print("Player fell off the map!")

    def draw(self):
        """Draw the game."""
        # Get screen shake offset
        shake_offset = self.screen_shake.get_offset()

        if self.state == GameState.MENU:
            self.ui.draw_main_menu(self.screen, self.menu_option)
            pygame.display.flip()
            return

        if self.state == GameState.SETTINGS:
            self.ui.draw_settings_menu(self.screen, self.settings)
            pygame.display.flip()
            return

        # Clear screen with modern dark background
        self.screen.fill((20, 22, 35))

        # Draw level with screen shake
        self.current_tilemap.draw(self.screen, shake_offset)

        # Draw player with screen shake
        self.player.draw(self.screen, shake_offset)

        # Draw particles (gameplay particles affected by shake)
        self.particle_manager.draw(self.screen, shake_offset)

        # Draw HUD (not affected by screen shake)
        if self.settings.get("game", "show_timer"):
            self.ui.draw_hud(self.screen, self.level_manager.level_number,
                            getattr(self.current_tilemap, "name", ""),
                            self.timer, self.gravity_manager.direction)

        # Draw FPS if enabled
        if self.settings.get("game", "show_fps"):
            fps = self.clock.get_fps()
            if self.ui.small_font:
                fps_text = f"FPS: {fps:.0f}"
                fps_surface = self.ui.small_font.render(fps_text, True, self.ui.colors["muted"])
                self.screen.blit(fps_surface, (self.screen_width - 100, self.screen_height - 30))

        # Draw state-specific UI
        if self.state == GameState.PAUSED:
            self.ui.draw_pause_menu(self.screen)
        elif self.state == GameState.LEVEL_COMPLETE:
            self.ui.draw_level_complete(self.screen, self.level_completion_time)
        elif self.state == GameState.DEAD:
            self.ui.draw_death_screen(self.screen)

        # Draw transitions on top
        self.transition_manager.draw(self.screen)

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
        fixed_dt = 1.0 / PHYSICS_TICK
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            dt = min(dt, 0.25)
            
            # Handle input
            self.handle_input()
            
            # Fixed timestep updates for stable physics
            self.accumulator += dt
            while self.accumulator >= fixed_dt:
                self.update(fixed_dt)
                self.accumulator -= fixed_dt
            
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
