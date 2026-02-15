"""Scene transition effects for state changes."""

import pygame
import math
from game.utils import ease_in_quad, ease_out_quad, clamp


class Transition:
    """Base class for scene transitions."""

    def __init__(self, duration):
        """Initialize transition.

        Args:
            duration: Transition duration in seconds
        """
        self.duration = duration
        self.timer = 0.0
        self.progress = 0.0
        self.active = False
        self.from_surface = None
        self.to_surface = None

    def start(self, from_surface=None, to_surface=None):
        """Start the transition.

        Args:
            from_surface: Surface to transition from (optional)
            to_surface: Surface to transition to (optional)
        """
        self.active = True
        self.timer = 0.0
        self.progress = 0.0
        self.from_surface = from_surface
        self.to_surface = to_surface

    def update(self, dt):
        """Update transition progress.

        Args:
            dt: Delta time in seconds

        Returns:
            True if transition is complete, False otherwise
        """
        if not self.active:
            return True

        self.timer += dt
        self.progress = clamp(self.timer / self.duration, 0.0, 1.0)

        if self.progress >= 1.0:
            self.active = False
            return True

        return False

    def draw(self, screen):
        """Draw transition effect.

        Args:
            screen: pygame.Surface to draw on
        """
        pass

    def is_active(self):
        """Check if transition is active.

        Returns:
            True if transition is in progress
        """
        return self.active


class FadeTransition(Transition):
    """Fade to black transition."""

    def __init__(self, duration=0.3, color=(0, 0, 0)):
        """Initialize fade transition.

        Args:
            duration: Fade duration in seconds
            color: Fade color (default black)
        """
        super().__init__(duration)
        self.color = color
        self.fade_out = True  # First half fades out, second half fades in

    def draw(self, screen):
        """Draw fade overlay.

        Args:
            screen: pygame.Surface to draw on
        """
        if not self.active:
            return

        # Create fading overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        # First half: fade out (alpha increases)
        # Second half: fade in (alpha decreases)
        if self.progress < 0.5:
            # Fade out
            alpha = int(255 * (self.progress * 2))
        else:
            # Fade in
            alpha = int(255 * (2 - self.progress * 2))

        overlay.fill((*self.color, alpha))
        screen.blit(overlay, (0, 0))

    def is_halfway(self):
        """Check if transition is halfway (fully faded).

        Returns:
            True if at the darkest point
        """
        return 0.4 < self.progress < 0.6


class SlideTransition(Transition):
    """Slide transition that moves screen in a direction."""

    def __init__(self, duration=0.4, direction="down"):
        """Initialize slide transition.

        Args:
            duration: Slide duration in seconds
            direction: Slide direction ("up", "down", "left", "right")
        """
        super().__init__(duration)
        self.direction = direction

    def draw(self, screen):
        """Draw slide transition.

        Args:
            screen: pygame.Surface to draw on
        """
        if not self.active or not self.from_surface:
            return

        width, height = screen.get_size()

        # Calculate offset based on direction and progress
        eased = ease_out_quad(self.progress)

        if self.direction == "down":
            offset_y = int(eased * height)
            screen.blit(self.from_surface, (0, offset_y))
        elif self.direction == "up":
            offset_y = int(-eased * height)
            screen.blit(self.from_surface, (0, offset_y))
        elif self.direction == "left":
            offset_x = int(-eased * width)
            screen.blit(self.from_surface, (offset_x, 0))
        elif self.direction == "right":
            offset_x = int(eased * width)
            screen.blit(self.from_surface, (offset_x, 0))


class CircleTransition(Transition):
    """Circular wipe transition expanding from center."""

    def __init__(self, duration=0.5, color=(0, 0, 0)):
        """Initialize circle transition.

        Args:
            duration: Transition duration in seconds
            color: Wipe color (default black)
        """
        super().__init__(duration)
        self.color = color
        self.expanding = True  # True for expand, False for contract

    def draw(self, screen):
        """Draw circle wipe.

        Args:
            screen: pygame.Surface to draw on
        """
        if not self.active:
            return

        width, height = screen.get_size()
        center_x = width // 2
        center_y = height // 2

        # Calculate max radius (diagonal from center to corner)
        max_radius = int(math.sqrt(center_x ** 2 + center_y ** 2)) + 10

        # Create mask surface
        mask = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        if self.expanding:
            # Circle expands (reveals content)
            # Fill mask, then cut out circle
            mask.fill((*self.color, 255))
            radius = int(ease_out_quad(self.progress) * max_radius)
            if radius < max_radius:
                # Draw transparent circle to cut out
                pygame.draw.circle(mask, (0, 0, 0, 0), (center_x, center_y), radius)
        else:
            # Circle contracts (covers content)
            radius = int((1 - ease_in_quad(self.progress)) * max_radius)
            pygame.draw.circle(mask, (*self.color, 255), (center_x, center_y), radius)

        screen.blit(mask, (0, 0))


class TransitionManager:
    """Manages scene transitions."""

    def __init__(self):
        """Initialize transition manager."""
        self.current_transition = None
        self.on_halfway_callback = None
        self.on_complete_callback = None

    def start_fade(self, duration=0.3, color=(0, 0, 0), on_halfway=None, on_complete=None):
        """Start a fade transition.

        Args:
            duration: Fade duration in seconds
            color: Fade color
            on_halfway: Callback when fade is halfway (fully dark)
            on_complete: Callback when fade is complete
        """
        self.current_transition = FadeTransition(duration, color)
        self.current_transition.start()
        self.on_halfway_callback = on_halfway
        self.on_complete_callback = on_complete

    def start_slide(self, from_surface, direction="down", duration=0.4, on_complete=None):
        """Start a slide transition.

        Args:
            from_surface: Surface to slide away
            direction: Slide direction
            duration: Slide duration
            on_complete: Callback when complete
        """
        self.current_transition = SlideTransition(duration, direction)
        self.current_transition.start(from_surface=from_surface)
        self.on_halfway_callback = None
        self.on_complete_callback = on_complete

    def start_circle(self, expanding=True, duration=0.5, color=(0, 0, 0), on_halfway=None, on_complete=None):
        """Start a circle wipe transition.

        Args:
            expanding: True to expand (reveal), False to contract (cover)
            duration: Transition duration
            color: Wipe color
            on_halfway: Callback at halfway point
            on_complete: Callback when complete
        """
        self.current_transition = CircleTransition(duration, color)
        self.current_transition.expanding = expanding
        self.current_transition.start()
        self.on_halfway_callback = on_halfway
        self.on_complete_callback = on_complete

    def update(self, dt):
        """Update current transition.

        Args:
            dt: Delta time in seconds
        """
        if not self.current_transition:
            return

        # Check if at halfway point for fade transition
        if isinstance(self.current_transition, FadeTransition):
            was_before_halfway = self.current_transition.progress < 0.5
            is_complete = self.current_transition.update(dt)
            is_after_halfway = self.current_transition.progress >= 0.5

            if was_before_halfway and is_after_halfway and self.on_halfway_callback:
                self.on_halfway_callback()
                self.on_halfway_callback = None  # Call only once
        else:
            is_complete = self.current_transition.update(dt)

        # Handle completion
        if is_complete:
            if self.on_complete_callback:
                self.on_complete_callback()
                self.on_complete_callback = None
            self.current_transition = None

    def draw(self, screen):
        """Draw current transition.

        Args:
            screen: pygame.Surface to draw on
        """
        if self.current_transition:
            self.current_transition.draw(screen)

    def is_active(self):
        """Check if a transition is currently active.

        Returns:
            True if transition is in progress
        """
        return self.current_transition is not None and self.current_transition.is_active()

    def skip(self):
        """Skip the current transition immediately."""
        if self.current_transition:
            self.current_transition.progress = 1.0
            self.current_transition.active = False

            if self.on_complete_callback:
                self.on_complete_callback()
                self.on_complete_callback = None

            self.current_transition = None
