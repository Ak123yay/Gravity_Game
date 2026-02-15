"""Reusable UI components for Gravity Control game."""

import pygame
from game.utils import lerp, clamp, ease_out_quad


class Button:
    """Interactive button component with hover and click states."""

    def __init__(self, rect, text, colors, font, on_click=None):
        """Initialize button.

        Args:
            rect: pygame.Rect for button position and size
            text: Button text
            colors: Dictionary with 'bg', 'bg_hover', 'text', 'border' colors
            font: pygame.Font for text
            on_click: Callback function when clicked
        """
        self.rect = rect
        self.text = text
        self.colors = colors
        self.font = font
        self.on_click = on_click
        self.hovered = False
        self.pressed = False
        self.hover_progress = 0.0

    def update(self, dt, mouse_pos):
        """Update button state.

        Args:
            dt: Delta time in seconds
            mouse_pos: Current mouse position tuple (x, y)
        """
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)

        # Smooth hover transition
        target = 1.0 if self.hovered else 0.0
        self.hover_progress = lerp(self.hover_progress, target, dt * 10)

    def handle_event(self, event):
        """Handle pygame event.

        Args:
            event: pygame event

        Returns:
            True if button was clicked, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.pressed = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.hovered:
                self.pressed = False
                if self.on_click:
                    self.on_click()
                return True
            self.pressed = False

        return False

    def draw(self, screen):
        """Draw button to screen.

        Args:
            screen: pygame.Surface to draw on
        """
        # Interpolate background color based on hover
        bg_color = self.colors['bg']
        bg_hover_color = self.colors.get('bg_hover', self.colors['bg'])

        if self.hover_progress > 0:
            r = int(lerp(bg_color[0], bg_hover_color[0],  self.hover_progress))
            g = int(lerp(bg_color[1], bg_hover_color[1], self.hover_progress))
            b = int(lerp(bg_color[2], bg_hover_color[2], self.hover_progress))
            current_bg = (r, g, b)
        else:
            current_bg = bg_color

        # Draw background with subtle scale when pressed
        draw_rect = self.rect.copy()
        if self.pressed:
            shrink = 2
            draw_rect.inflate_ip(-shrink * 2, -shrink * 2)

        pygame.draw.rect(screen, current_bg, draw_rect, border_radius=2)

        # Draw border
        if 'border' in self.colors:
            pygame.draw.rect(screen, self.colors['border'], draw_rect, 2, border_radius=2)

        # Draw glow when hovered
        if self.hover_progress > 0.2 and 'glow' in self.colors:
            glow_color = self.colors['glow']
            glow_alpha = int(clamp(glow_color[3] if len(glow_color) > 3 else 40, 0, 255) * self.hover_progress)
            glow_surf = pygame.Surface((draw_rect.width + 8, draw_rect.height + 8), pygame.SRCALPHA)
            glow_rect = pygame.Rect(2, 2, draw_rect.width + 4, draw_rect.height + 4)
            pygame.draw.rect(glow_surf, (*glow_color[:3], glow_alpha), glow_rect, 2, border_radius=3)
            screen.blit(glow_surf, (draw_rect.x - 4, draw_rect.y - 4))

        # Draw text
        text_surf = self.font.render(self.text, True, self.colors['text'])
        text_rect = text_surf.get_rect(center=draw_rect.center)
        screen.blit(text_surf, text_rect)


class Slider:
    """Horizontal slider component for value selection."""

    def __init__(self, rect, value, min_val, max_val, colors, font, label="", on_change=None):
        """Initialize slider.

        Args:
            rect: pygame.Rect for slider position and size
            value: Current value
            min_val: Minimum value
            max_val: Maximum value
            colors: Dictionary with 'track', 'fill', 'handle', 'text' colors
            font: pygame.Font for label and value
            label: Label text
            on_change: Callback function(value) when value changes
        """
        self.rect = rect
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.colors = colors
        self.font = font
        self.label = label
        self.on_change = on_change
        self.dragging = False
        self.hovered = False

        # Calculate track and handle rects
        self.track_height = 4
        self.handle_radius = 8
        self._update_rects()

    def _update_rects(self):
        """Update track and handle rectangles."""
        # Track is in the middle of the rect
        self.track_rect = pygame.Rect(
            self.rect.x,
            self.rect.centery - self.track_height // 2,
            self.rect.width,
            self.track_height
        )

        # Calculate handle position based on value
        normalized = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + int(normalized * self.rect.width)
        self.handle_pos = (handle_x, self.rect.centery)

    def update(self, dt, mouse_pos):
        """Update slider state.

        Args:
            dt: Delta time in seconds
            mouse_pos: Current mouse position tuple (x, y)
        """
        # Check if mouse is over handle
        dx = mouse_pos[0] - self.handle_pos[0]
        dy = mouse_pos[1] - self.handle_pos[1]
        dist = (dx * dx + dy * dy) ** 0.5
        self.hovered = dist < self.handle_radius * 1.5

    def handle_event(self, event):
        """Handle pygame event.

        Args:
            event: pygame event

        Returns:
            True if value changed, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered or self.track_rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value_from_mouse(event.pos[0])
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False

        if event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value_from_mouse(event.pos[0])
            return True

        return False

    def _update_value_from_mouse(self, mouse_x):
        """Update value based on mouse X position.

        Args:
            mouse_x: Mouse X coordinate
        """
        normalized = clamp((mouse_x - self.rect.x) / self.rect.width, 0.0, 1.0)
        new_value = self.min_val + normalized * (self.max_val - self.min_val)

        if isinstance(self.min_val, int) and isinstance(self.max_val, int):
            new_value = int(new_value)

        if new_value != self.value:
            self.value = new_value
            self._update_rects()
            if self.on_change:
                self.on_change(self.value)

    def draw(self, screen):
        """Draw slider to screen.

        Args:
           screen: pygame.Surface to draw on
        """
        # Draw label if present
        if self.label:
            label_surf = self.font.render(self.label, True, self.colors['text'])
            label_rect = label_surf.get_rect(midleft=(self.rect.x, self.rect.y + 10))
            screen.blit(label_surf, label_rect)

        # Draw track background
        pygame.draw.rect(screen, self.colors['track'], self.track_rect, border_radius=2)

        # Draw filled portion
        normalized = (self.value - self.min_val) / (self.max_val - self.min_val)
        fill_width = int(normalized * self.track_rect.width)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.track_rect.x, self.track_rect.y, fill_width, self.track_rect.height)
            pygame.draw.rect(screen, self.colors['fill'], fill_rect, border_radius=2)

        # Draw handle
        handle_radius = self.handle_radius
        if self.dragging:
            handle_radius = int(handle_radius * 1.2)

        pygame.draw.circle(screen, self.colors['handle'], self.handle_pos, handle_radius)

        # Draw handle border
        if 'handle_border' in self.colors:
            pygame.draw.circle(screen, self.colors['handle_border'], self.handle_pos, handle_radius, 2)

        # Draw value
        value_text = f"{int(self.value)}" if isinstance(self.value, int) else f"{self.value:.1f}"
        value_surf = self.font.render(value_text, True, self.colors['text'])
        value_rect = value_surf.get_rect(midright=(self.rect.right, self.rect.y + 10))
        screen.blit(value_surf, value_rect)


class Toggle:
    """Toggle switch component for boolean values."""

    def __init__(self, rect, value, colors, font, label="", on_change=None):
        """Initialize toggle.

        Args:
            rect: pygame.Rect for toggle position
            value: Current boolean value
            colors: Dictionary with 'bg_off', 'bg_on', 'handle', 'text' colors
            font: pygame.Font for label
            label: Label text
            on_change: Callback function(value) when toggled
        """
        self.rect = rect
        self.value = value
        self.colors = colors
        self.font = font
        self.label = label
        self.on_change = on_change
        self.hovered = False
        self.animation_progress = 1.0 if value else 0.0

        # Toggle switch dimensions
        self.switch_width = 48
        self.switch_height = 24
        self.switch_rect = pygame.Rect(self.rect.right - self.switch_width, self.rect.y, self.switch_width, self.switch_height)

    def update(self, dt, mouse_pos):
        """Update toggle state.

        Args:
            dt: Delta time in seconds
            mouse_pos: Current mouse position tuple (x, y)
        """
        self.hovered = self.switch_rect.collidepoint(mouse_pos)

        # Animate handle position
        target = 1.0 if self.value else 0.0
        self.animation_progress = lerp(self.animation_progress, target, dt * 10)

    def handle_event(self, event):
        """Handle pygame event.

        Args:
            event: pygame event

        Returns:
            True if toggle changed, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.value = not self.value
                if self.on_change:
                    self.on_change(self.value)
                return True

        return False

    def draw(self, screen):
        """Draw toggle to screen.

        Args:
            screen: pygame.Surface to draw on
        """
        # Draw label
        if self.label:
            label_surf = self.font.render(self.label, True, self.colors['text'])
            label_rect = label_surf.get_rect(midleft=(self.rect.x, self.rect.centery))
            screen.blit(label_surf, label_rect)

        # Interpolate background color
        bg_off = self.colors['bg_off']
        bg_on = self.colors['bg_on']
        r = int(lerp(bg_off[0], bg_on[0], self.animation_progress))
        g = int(lerp(bg_off[1], bg_on[1], self.animation_progress))
        b = int(lerp(bg_off[2], bg_on[2], self.animation_progress))
        bg_color = (r, g, b)

        # Draw switch background
        pygame.draw.rect(screen, bg_color, self.switch_rect, border_radius=self.switch_height // 2)

        # Draw handle
        handle_radius = self.switch_height // 2 - 3
        handle_x_off = self.switch_rect.x + handle_radius + 3
        handle_x_on = self.switch_rect.right - handle_radius - 3
        handle_x = int(lerp(handle_x_off, handle_x_on, self.animation_progress))
        handle_pos = (handle_x, self.switch_rect.centery)

        pygame.draw.circle(screen, self.colors['handle'], handle_pos, handle_radius)
