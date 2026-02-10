"""UI and HUD components for Gravity Control game."""

import pygame


class UI:
    """Manages UI elements and HUD."""
    
    def __init__(self, screen_width, screen_height):
        """Initialize the UI manager.
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = None
        self.small_font = None
        
        # Try to initialize fonts
        try:
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        except:
            print("Warning: Could not load fonts")
    
    def draw_hud(self, screen, level_number, timer, gravity_direction):
        """Draw the heads-up display.
        
        Args:
            screen: Pygame surface to draw on
            level_number: Current level number
            timer: Current timer value in seconds
            gravity_direction: Current gravity direction string
        """
        if not self.small_font:
            return
        
        # Draw level number
        level_text = self.small_font.render(f"Level {level_number}", True, (255, 255, 255))
        screen.blit(level_text, (10, 10))
        
        # Draw timer
        timer_text = self.small_font.render(f"Time: {timer:.1f}s", True, (255, 255, 255))
        screen.blit(timer_text, (10, 40))
        
        # Draw gravity direction indicator
        gravity_text = self.small_font.render(f"Gravity: {gravity_direction.upper()}", True, (255, 255, 0))
        screen.blit(gravity_text, (10, 70))
        
        # Draw controls hint
        hint_text = self.small_font.render("Arrow keys: Rotate gravity | R: Restart | ESC: Pause", True, (150, 150, 150))
        screen.blit(hint_text, (10, self.screen_height - 30))
    
    def draw_message(self, screen, message, y_offset=0):
        """Draw a centered message on screen.
        
        Args:
            screen: Pygame surface to draw on
            message: Message text to display
            y_offset: Vertical offset from center
        """
        if not self.font:
            return
        
        text = self.font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + y_offset))
        
        # Draw background
        padding = 20
        bg_rect = pygame.Rect(text_rect.x - padding, text_rect.y - padding,
                             text_rect.width + padding * 2, text_rect.height + padding * 2)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
        
        screen.blit(text, text_rect)
    
    def draw_pause_menu(self, screen):
        """Draw the pause menu.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw pause text
        self.draw_message(screen, "PAUSED", -50)
        
        if self.small_font:
            resume_text = self.small_font.render("Press ESC to resume", True, (200, 200, 200))
            resume_rect = resume_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
            screen.blit(resume_text, resume_rect)
            
            restart_text = self.small_font.render("Press R to restart level", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
            screen.blit(restart_text, restart_rect)
    
    def draw_level_complete(self, screen, time_taken):
        """Draw the level complete screen.
        
        Args:
            screen: Pygame surface to draw on
            time_taken: Time taken to complete the level
        """
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 50, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw completion message
        self.draw_message(screen, "LEVEL COMPLETE!", -50)
        
        if self.small_font:
            time_text = self.small_font.render(f"Time: {time_taken:.2f}s", True, (255, 255, 0))
            time_rect = time_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
            screen.blit(time_text, time_rect)
            
            continue_text = self.small_font.render("Press SPACE to continue", True, (200, 200, 200))
            continue_rect = continue_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 60))
            screen.blit(continue_text, continue_rect)
    
    def draw_death_screen(self, screen):
        """Draw the death screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw semi-transparent red overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(100)
        overlay.fill((100, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw death message
        self.draw_message(screen, "YOU DIED", -30)
        
        if self.small_font:
            restart_text = self.small_font.render("Press R to restart", True, (255, 200, 200))
            restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 30))
            screen.blit(restart_text, restart_rect)
