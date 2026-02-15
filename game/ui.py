"""UI and HUD components for Gravity Control game."""

import pygame
import math


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
        self.animation_time = 0

        # Modern, vibrant color scheme with better contrast
        self.colors = {
            "bg": (15, 15, 25),  # Darker, richer background
            "bg_gradient": (25, 25, 40),  # For gradient effects
            "panel": (32, 35, 50),  # Darker panels
            "panel_light": (45, 50, 70),  # Lighter panel shade
            "panel_border": (85, 95, 130),  # Brighter borders
            "panel_glow": (100, 120, 180, 40),  # Glow effect with alpha
            "accent": (80, 180, 255),  # Brighter cyan
            "accent_bright": (120, 220, 255),  # Very bright cyan
            "accent_alt": (255, 180, 70),  # Vibrant orange
            "accent_alt_bright": (255, 220, 100),  # Bright orange
            "text": (245, 250, 255),  # Crisp white-blue
            "text_shadow": (10, 10, 20),  # Text shadow
            "muted": (150, 160, 180),  # Muted text
            "success": (80, 230, 150),  # Vibrant green
            "success_glow": (80, 230, 150, 60),
            "danger": (255, 80, 100),  # Vibrant red
            "danger_glow": (255, 80, 100, 60),
            "grid": (25, 28, 42),  # Subtle grid
            "grid_accent": (40, 45, 65)  # Accented grid lines
        }

        try:
            # Try to use system fonts for better appearance
            self.title_font = pygame.font.SysFont('arial', 76, bold=True)
            self.header_font = pygame.font.SysFont('arial', 42, bold=True)
            self.body_font = pygame.font.SysFont('arial', 28, bold=False)
            self.small_font = pygame.font.SysFont('arial', 20, bold=False)
        except pygame.error:
            # Fallback to default font with larger sizes
            try:
                self.title_font = pygame.font.Font(None, 78)
                self.header_font = pygame.font.Font(None, 44)
                self.body_font = pygame.font.Font(None, 32)
                self.small_font = pygame.font.Font(None, 24)
            except pygame.error as e:
                print(f"Warning: Could not load fonts: {e}")

    def update(self, dt):
        """Update UI animations."""
        self.animation_time += dt

    def _draw_glow(self, screen, rect, glow_color, glow_size=6):
        """Draw a subtle glow effect around a rect."""
        glow_surface = pygame.Surface((rect.width + glow_size * 2, rect.height + glow_size * 2), pygame.SRCALPHA)
        for i in range(glow_size):
            alpha = glow_color[3] if len(glow_color) > 3 else 40
            alpha = int(alpha * (1 - i / glow_size))
            color = (*glow_color[:3], alpha)
            glow_rect = pygame.Rect(i, i, rect.width + (glow_size - i) * 2, rect.height + (glow_size - i) * 2)
            pygame.draw.rect(glow_surface, color, glow_rect, 1)
        screen.blit(glow_surface, (rect.x - glow_size, rect.y - glow_size))

    def _draw_panel(self, screen, rect, fill_color, border_color=None, alpha=None, glow=False):
        """Draw a panel with optional glow and border effects."""
        # Draw glow effect first (behind panel)
        if glow:
            self._draw_glow(screen, rect, self.colors["panel_glow"])

        # Draw panel
        if alpha is not None:
            panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            panel.fill((*fill_color, alpha))
            screen.blit(panel, rect.topleft)
        else:
            pygame.draw.rect(screen, fill_color, rect)

        # Draw inner highlight for depth
        if rect.height > 8 and rect.width > 8:
            highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
            pygame.draw.line(screen, self.colors["panel_light"],
                           (highlight_rect.left, highlight_rect.top),
                           (highlight_rect.right, highlight_rect.top), 1)
            pygame.draw.line(screen, self.colors["panel_light"],
                           (highlight_rect.left, highlight_rect.top),
                           (highlight_rect.left, highlight_rect.bottom), 1)

        # Draw border
        if border_color:
            pygame.draw.rect(screen, border_color, rect, 2)

    def _draw_text(self, screen, font, text, color, center=None, topleft=None, shadow=True, shadow_offset=3):
        """Draw text with optional shadow for better readability."""
        if not font:
            return

        # Always draw shadow for better contrast unless explicitly disabled
        if shadow:
            shadow_surface = font.render(text, True, self.colors["text_shadow"])
            shadow_pos = shadow_surface.get_rect()
            if center:
                shadow_pos.center = (center[0] + shadow_offset, center[1] + shadow_offset)
            elif topleft:
                shadow_pos.topleft = (topleft[0] + shadow_offset, topleft[1] + shadow_offset)
            screen.blit(shadow_surface, shadow_pos)

        # Draw main text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = center
        elif topleft:
            text_rect.topleft = topleft
        screen.blit(text_surface, text_rect)

    def _draw_background(self, screen):
        """Draw enhanced background with gradient and dynamic grid."""
        # Draw gradient background
        for y in range(0, self.screen_height, 4):
            ratio = y / self.screen_height
            color = tuple(int(self.colors["bg"][i] + (self.colors["bg_gradient"][i] - self.colors["bg"][i]) * ratio) for i in range(3))
            pygame.draw.line(screen, color, (0, y), (self.screen_width, y), 4)

        # Draw dynamic grid with subtle animation
        spacing = 40
        offset = int(self.animation_time * 10) % spacing

        # Vertical lines
        for x in range(-offset, self.screen_width, spacing):
            is_major = (x + offset) % (spacing * 4) == 0
            color = self.colors["grid_accent"] if is_major else self.colors["grid"]
            width = 1 if is_major else 1
            pygame.draw.line(screen, color, (x, 0), (x, self.screen_height), width)

        # Horizontal lines
        for y in range(-offset, self.screen_height, spacing):
            is_major = (y + offset) % (spacing * 4) == 0
            color = self.colors["grid_accent"] if is_major else self.colors["grid"]
            width = 1 if is_major else 1
            pygame.draw.line(screen, color, (0, y), (self.screen_width, y), width)

    def draw_hud(self, screen, level_number, level_name, timer, gravity_direction):
        """Draw the heads-up display with modern styling."""
        if not self.small_font:
            return

        level_label = level_name or f"Level {level_number}"

        # Top HUD bar with glow
        top_rect = pygame.Rect(16, 12, self.screen_width - 32, 64)
        self._draw_panel(screen, top_rect, self.colors["panel"], self.colors["panel_border"], alpha=240, glow=True)

        # Level name on left
        self._draw_text(screen, self.body_font, level_label, self.colors["accent_bright"], topleft=(32, 26))

        # Timer in center with pulse effect
        pulse = 1.0 + math.sin(self.animation_time * 3) * 0.1
        timer_text = f"{timer:0.1f}s"
        timer_size = int(self.body_font.get_height() * pulse)
        timer_y = 40 - (timer_size - self.body_font.get_height()) // 2
        self._draw_text(screen, self.body_font, timer_text, self.colors["accent_alt_bright"],
                        center=(self.screen_width // 2, timer_y))

        # Gravity indicator on right
        gravity_label = f"Gravity: {gravity_direction.upper()}"
        self._draw_text(screen, self.small_font, gravity_label, self.colors["text"],
                        topleft=(self.screen_width - 260, 28))
        self.draw_gravity_indicator(screen, gravity_direction, self.screen_width - 60, 44)

        # Bottom control hints bar
        bottom_rect = pygame.Rect(16, self.screen_height - 48, self.screen_width - 32, 36)
        self._draw_panel(screen, bottom_rect, self.colors["panel"], self.colors["panel_border"], alpha=220)
        self._draw_text(screen, self.small_font,
                        "Arrows: Gravity   R: Restart   ESC: Menu",
                        self.colors["muted"], center=bottom_rect.center, shadow=False)

    def draw_gravity_indicator(self, screen, direction, x, y):
        """Draw an enhanced visual arrow for gravity direction."""
        # Outer glow circle
        pygame.draw.circle(screen, self.colors["panel_border"], (x, y), 18, 2)
        # Background circle
        pygame.draw.circle(screen, self.colors["panel"], (x, y), 16)
        # Inner highlight
        pygame.draw.circle(screen, self.colors["panel_light"], (x - 2, y - 2), 6)

        # Direction arrow with better styling
        size = 9
        if direction == "down":
            points = [(x, y + size), (x - size, y - size), (x + size, y - size)]
        elif direction == "up":
            points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
        elif direction == "left":
            points = [(x - size, y), (x + size, y - size), (x + size, y + size)]
        else:
            points = [(x + size, y), (x - size, y - size), (x - size, y + size)]

        # Draw arrow with outline
        pygame.draw.polygon(screen, self.colors["text_shadow"], [(p[0] + 1, p[1] + 1) for p in points])
        pygame.draw.polygon(screen, self.colors["accent_alt_bright"], points)

    def draw_main_menu(self, screen, selected_option):
        """Draw the main menu with enhanced visuals."""
        self._draw_background(screen)

        # Animated title with pulse effect
        if self.title_font:
            pulse = 1.0 + math.sin(self.animation_time * 2) * 0.05
            title_color = tuple(int(c * pulse) if c < 255 else 255 for c in self.colors["accent_bright"])
            self._draw_text(screen, self.title_font, "GRAVITY CONTROL", title_color,
                            center=(self.screen_width // 2, 150), shadow=True, shadow_offset=5)

        # Menu panel with glow
        menu_rect = pygame.Rect(self.screen_width // 2 - 200, 260, 400, 200)
        self._draw_panel(screen, menu_rect, self.colors["panel"], self.colors["panel_border"], alpha=240, glow=True)

        # Menu options with better styling
        options = ["Start Game", "Quit"]
        for i, option in enumerate(options):
            if i == selected_option:
                # Selected option with glow effect
                color = self.colors["accent_alt_bright"]
                text_pulse = 1.0 + math.sin(self.animation_time * 5) * 0.15
                y_pos = 330 + i * 70
                # Draw selection indicator
                indicator_rect = pygame.Rect(self.screen_width // 2 - 150, y_pos - 20, 300, 50)
                self._draw_glow(screen, indicator_rect, (*self.colors["accent_alt"], 80))
                pygame.draw.rect(screen, (*self.colors["accent_alt"], 30), indicator_rect)
            else:
                color = self.colors["text"]
                y_pos = 330 + i * 70

            self._draw_text(screen, self.body_font, option, color,
                            center=(self.screen_width // 2, y_pos))

        # Hint panel at bottom
        hint_rect = pygame.Rect(self.screen_width // 2 - 220, 480, 440, 44)
        self._draw_panel(screen, hint_rect, self.colors["panel"], self.colors["panel_border"], alpha=220)
        self._draw_text(screen, self.small_font, "ENTER: Select   UP/DOWN: Navigate",
                        self.colors["muted"], center=hint_rect.center, shadow=False)

    def draw_message(self, screen, message, y_offset=0, tone="default"):
        """Draw a centered message on screen with enhanced styling."""
        if not self.body_font:
            return

        # Choose colors based on tone
        if tone == "danger":
            color = self.colors["danger"]
            glow_color = self.colors["danger_glow"]
        elif tone == "success":
            color = self.colors["success"]
            glow_color = self.colors["success_glow"]
        else:
            color = self.colors["text"]
            glow_color = self.colors["panel_glow"]

        # Measure text
        text_surface = self.body_font.render(message, True, color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2,
                                                  self.screen_height // 2 + y_offset))

        # Draw background panel with glow
        padding = 24
        bg_rect = pygame.Rect(text_rect.x - padding, text_rect.y - padding,
                              text_rect.width + padding * 2, text_rect.height + padding * 2)
        self._draw_panel(screen, bg_rect, self.colors["panel"], self.colors["panel_border"], alpha=250, glow=True)

        # Draw text
        screen.blit(text_surface, text_rect)

    def draw_pause_menu(self, screen):
        """Draw the pause menu with enhanced overlay."""
        # Dark overlay with transparency
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((5, 5, 10, 200))
        screen.blit(overlay, (0, 0))

        # Title
        self.draw_message(screen, "PAUSED", -70)

        # Instructions
        if self.small_font:
            y_base = self.screen_height // 2 + 10
            self._draw_text(screen, self.body_font, "ESC: Resume", self.colors["accent_bright"],
                            center=(self.screen_width // 2, y_base))
            self._draw_text(screen, self.small_font, "R: Restart   Q: Main Menu",
                            self.colors["muted"], center=(self.screen_width // 2, y_base + 50))

    def draw_level_complete(self, screen, time_taken):
        """Draw the level complete screen with celebratory effects."""
        # Greenish overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 60, 30, 180))
        screen.blit(overlay, (0, 0))

        # Success message
        self.draw_message(screen, "LEVEL COMPLETE!", -70, tone="success")

        # Time display
        if self.small_font:
            y_base = self.screen_height // 2 + 10
            time_text = f"Time: {time_taken:.2f}s"
            self._draw_text(screen, self.body_font, time_text, self.colors["accent_alt_bright"],
                            center=(self.screen_width // 2, y_base))
            self._draw_text(screen, self.small_font, "SPACE: Continue",
                            self.colors["success"], center=(self.screen_width // 2, y_base + 60))

    def draw_death_screen(self, screen):
        """Draw the death screen with dramatic effect."""
        # Reddish overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((80, 10, 10, 200))
        screen.blit(overlay, (0, 0))

        # Death message
        self.draw_message(screen, "YOU DIED", -50, tone="danger")

        # Restart hint
        if self.small_font:
            self._draw_text(screen, self.small_font, "R: Restart",
                            self.colors["danger"], center=(self.screen_width // 2, self.screen_height // 2 + 40))
