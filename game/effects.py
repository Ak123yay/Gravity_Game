"""Visual effects like screen shake and camera effects."""

import random


class ScreenShake:
    """Manages screen shake effect for impact and feedback."""

    def __init__(self):
        """Initialize screen shake effect."""
        self.intensity = 0.0
        self.duration = 0.0
        self.timer = 0.0
        self.offset_x = 0
        self.offset_y = 0
        self.enabled = True

    def trigger(self, intensity, duration):
        """Trigger screen shake effect.

        Args:
            intensity: Shake intensity in pixels (e.g., 10 for strong shake)
            duration: Duration in seconds (e.g., 0.25)
        """
        if not self.enabled:
            return

        self.intensity = intensity
        self.duration = duration
        self.timer = 0.0

    def update(self, dt):
        """Update screen shake effect.

        Args:
            dt: Delta time in seconds
        """
        if self.timer < self.duration:
            self.timer += dt

            # Calculate decay factor (shake gets weaker over time)
            progress = self.timer / self.duration
            decay = 1.0 - progress

            # Apply random offset with decay
            current_intensity = self.intensity * decay
            self.offset_x = random.uniform(-current_intensity, current_intensity)
            self.offset_y = random.uniform(-current_intensity, current_intensity)
        else:
            # Shake finished, reset
            self.offset_x = 0
            self.offset_y = 0

    def get_offset(self):
        """Get current screen shake offset.

        Returns:
            Tuple (offset_x, offset_y) in pixels
        """
        return (int(self.offset_x), int(self.offset_y))

    def is_shaking(self):
        """Check if currently shaking.

        Returns:
            True if shake effect is active
        """
        return self.timer < self.duration

    def reset(self):
        """Reset screen shake to idle state."""
        self.intensity = 0.0
        self.duration = 0.0
        self.timer = 0.0
        self.offset_x = 0
        self.offset_y = 0

    def set_enabled(self, enabled):
        """Enable or disable screen shake.

        Args:
            enabled: True to enable, False to disable
        """
        self.enabled = enabled
        if not enabled:
            self.reset()


class Camera:
    """Camera system with smooth following and bounds."""

    def __init__(self, screen_width, screen_height, world_width=None, world_height=None):
        """Initialize camera.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            world_width: World width in pixels (None for no bounds)
            world_height: World height in pixels (None for no bounds)
        """
        self.x = 0.0
        self.y = 0.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height
        self.target_x = 0.0
        self.target_y = 0.0
        self.smoothing = 0.1  # Lower = smoother, higher = snappier

    def follow(self, target_x, target_y, smoothing=None):
        """Set camera to follow a target position.

        Args:
            target_x: Target X position
            target_y: Target Y position
            smoothing: Optional smoothing factor (0.0 to 1.0)
        """
        if smoothing is not None:
            self.smoothing = smoothing

        self.target_x = target_x - self.screen_width // 2
        self.target_y = target_y - self.screen_height // 2

    def update(self, dt):
        """Update camera position with smooth interpolation.

        Args:
            dt: Delta time in seconds
        """
        # Smooth lerp to target
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing

        # Apply bounds if world size is set
        if self.world_width is not None:
            max_x = max(0, self.world_width - self.screen_width)
            self.x = max(0, min(self.x, max_x))
            self.target_x = max(0, min(self.target_x, max_x))

        if self.world_height is not None:
            max_y = max(0, self.world_height - self.screen_height)
            self.y = max(0, min(self.y, max_y))
            self.target_y = max(0, min(self.target_y, max_y))

    def get_offset(self):
        """Get camera offset for rendering.

        Returns:
            Tuple (-camera_x, -camera_y) for rendering offset
        """
        return (-int(self.x), -int(self.y))

    def apply(self, x, y):
        """Apply camera offset to world coordinates.

        Args:
            x: World X coordinate
            y: World Y coordinate

        Returns:
            Tuple (screen_x, screen_y)
        """
        return (int(x - self.x), int(y - self.y))

    def reset(self, x=0, y=0):
        """Reset camera to position.

        Args:
            x: X position
            y: Y position
        """
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
