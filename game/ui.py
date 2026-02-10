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
        self.title_font = None
        self.header_font = None
        self.body_font = None
        self.small_font = None

        self.colors = {
            "bg": (22, 24, 32),
            "panel": (36, 38, 52),
            "panel_border": (70, 75, 95),
            "accent": (100, 200, 255),
            "accent_alt": (255, 210, 120),
            "text": (230, 230, 240),
            "muted": (160, 170, 190),
            "success": (90, 210, 140),
            "danger": (220, 90, 90),
            "grid": (30, 34, 46)
        }

        try:
            self.title_font = pygame.font.Font(None, 72)
            self.header_font = pygame.font.Font(None, 40)
            self.body_font = pygame.font.Font(None, 30)
            self.small_font = pygame.font.Font(None, 22)
        except pygame.error as e:
            print(f"Warning: Could not load fonts: {e}")

    def _draw_panel(self, screen, rect, fill_color, border_color=None, alpha=None):
        if alpha is not None:
            panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            panel.fill((*fill_color, alpha))
            screen.blit(panel, rect.topleft)
        else:
            pygame.draw.rect(screen, fill_color, rect)

        if border_color:
            pygame.draw.rect(screen, border_color, rect, 2)

    def _draw_text(self, screen, font, text, color, center=None, topleft=None, shadow=False):
        if not font:
            return

        if shadow:
            shadow_surface = font.render(text, True, (0, 0, 0))
            shadow_pos = shadow_surface.get_rect()
            if center:
                shadow_pos.center = (center[0] + 2, center[1] + 2)
            elif topleft:
                shadow_pos.topleft = (topleft[0] + 2, topleft[1] + 2)
            screen.blit(shadow_surface, shadow_pos)

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = center
        elif topleft:
            text_rect.topleft = topleft
        screen.blit(text_surface, text_rect)

    def _draw_background(self, screen):
        screen.fill(self.colors["bg"])
        spacing = 40
        for x in range(0, self.screen_width, spacing):
            pygame.draw.line(screen, self.colors["grid"], (x, 0), (x, self.screen_height))
        for y in range(0, self.screen_height, spacing):
            pygame.draw.line(screen, self.colors["grid"], (0, y), (self.screen_width, y))

    def draw_hud(self, screen, level_number, level_name, timer, gravity_direction):
        """Draw the heads-up display."""
        if not self.small_font:
            return

        level_label = level_name or f"Level {level_number}"

        top_rect = pygame.Rect(12, 10, self.screen_width - 24, 56)
        self._draw_panel(screen, top_rect, self.colors["panel"], self.colors["panel_border"], alpha=230)

        self._draw_text(screen, self.body_font, level_label, self.colors["accent"], topleft=(26, 22))
        timer_text = f"{timer:0.1f}s"
        self._draw_text(screen, self.body_font, timer_text, self.colors["accent_alt"],
                        center=(self.screen_width // 2, 38))

        gravity_label = f"Gravity {gravity_direction.upper()}"
        self._draw_text(screen, self.small_font, gravity_label, self.colors["text"],
                        topleft=(self.screen_width - 240, 26))
        self.draw_gravity_indicator(screen, gravity_direction, self.screen_width - 50, 38)

        bottom_rect = pygame.Rect(12, self.screen_height - 44, self.screen_width - 24, 30)
        self._draw_panel(screen, bottom_rect, self.colors["panel"], self.colors["panel_border"], alpha=200)
        self._draw_text(screen, self.small_font,
                        "Arrows: Gravity   R: Restart   ESC: Menu",
                        self.colors["muted"], center=bottom_rect.center)

    def draw_gravity_indicator(self, screen, direction, x, y):
        """Draw a visual arrow for gravity direction."""
        pygame.draw.circle(screen, self.colors["panel_border"], (x, y), 14)
        pygame.draw.circle(screen, self.colors["panel"], (x, y), 12)

        size = 8
        if direction == "down":
            points = [(x, y + size), (x - size, y - size), (x + size, y - size)]
        elif direction == "up":
            points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
        elif direction == "left":
            points = [(x - size, y), (x + size, y - size), (x + size, y + size)]
        else:
            points = [(x + size, y), (x - size, y - size), (x - size, y + size)]

        pygame.draw.polygon(screen, self.colors["accent_alt"], points)

    def draw_main_menu(self, screen, selected_option):
        """Draw the main menu."""
        self._draw_background(screen)

        if self.title_font:
            self._draw_text(screen, self.title_font, "GRAVITY CONTROL", self.colors["accent"],
                            center=(self.screen_width // 2, 140), shadow=True)

        menu_rect = pygame.Rect(self.screen_width // 2 - 180, 240, 360, 180)
        self._draw_panel(screen, menu_rect, self.colors["panel"], self.colors["panel_border"], alpha=230)

        options = ["Start Game", "Quit"]
        for i, option in enumerate(options):
            color = self.colors["accent_alt"] if i == selected_option else self.colors["text"]
            self._draw_text(screen, self.body_font, option, color,
                            center=(self.screen_width // 2, 290 + i * 60))

        hint_rect = pygame.Rect(self.screen_width // 2 - 200, 440, 400, 36)
        self._draw_panel(screen, hint_rect, self.colors["panel"], self.colors["panel_border"], alpha=200)
        self._draw_text(screen, self.small_font, "ENTER: Select   UP/DOWN: Navigate",
                        self.colors["muted"], center=hint_rect.center)

    def draw_message(self, screen, message, y_offset=0, tone="default"):
        """Draw a centered message on screen."""
        if not self.body_font:
            return

        color = self.colors["text"]
        if tone == "danger":
            color = self.colors["danger"]
        elif tone == "success":
            color = self.colors["success"]

        text_surface = self.body_font.render(message, True, color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2,
                                                  self.screen_height // 2 + y_offset))
        padding = 18
        bg_rect = pygame.Rect(text_rect.x - padding, text_rect.y - padding,
                              text_rect.width + padding * 2, text_rect.height + padding * 2)
        self._draw_panel(screen, bg_rect, self.colors["panel"], self.colors["panel_border"], alpha=230)
        screen.blit(text_surface, text_rect)

    def draw_pause_menu(self, screen):
        """Draw the pause menu."""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 180))
        screen.blit(overlay, (0, 0))

        self.draw_message(screen, "PAUSED", -50)

        if self.small_font:
            self._draw_text(screen, self.small_font, "ESC: Resume", self.colors["muted"],
                            center=(self.screen_width // 2, self.screen_height // 2 + 20))
            self._draw_text(screen, self.small_font, "R: Restart   Q: Main Menu",
                            self.colors["muted"], center=(self.screen_width // 2, self.screen_height // 2 + 50))

    def draw_level_complete(self, screen, time_taken):
        """Draw the level complete screen."""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 50, 20, 170))
        screen.blit(overlay, (0, 0))

        self.draw_message(screen, "LEVEL COMPLETE!", -50, tone="success")

        if self.small_font:
            self._draw_text(screen, self.small_font, f"Time: {time_taken:.2f}s", self.colors["text"],
                            center=(self.screen_width // 2, self.screen_height // 2 + 20))
            self._draw_text(screen, self.small_font, "SPACE: Continue",
                            self.colors["muted"], center=(self.screen_width // 2, self.screen_height // 2 + 50))

    def draw_death_screen(self, screen):
        """Draw the death screen."""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((60, 10, 10, 180))
        screen.blit(overlay, (0, 0))

        self.draw_message(screen, "YOU DIED", -40, tone="danger")

        if self.small_font:
            self._draw_text(screen, self.small_font, "R: Restart",
                            self.colors["muted"], center=(self.screen_width // 2, self.screen_height // 2 + 30))
