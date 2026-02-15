"""Utility functions for animations and calculations."""

import math


def lerp(start, end, t):
    """Linear interpolation between start and end.

    Args:
        start: Starting value
        end: Ending value
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated value
    """
    return start + (end - start) * t


def clamp(value, min_val, max_val):
    """Clamp a value between min and max.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def ease_in_quad(t):
    """Quadratic ease-in easing function.

    Args:
        t: Progress value (0.0 to 1.0)

    Returns:
        Eased value
    """
    return t * t


def ease_out_quad(t):
    """Quadratic ease-out easing function.

    Args:
        t: Progress value (0.0 to 1.0)

    Returns:
        Eased value
    """
    return t * (2 - t)


def ease_in_out_quad(t):
    """Quadratic ease-in-out easing function.

    Args:
        t: Progress value (0.0 to 1.0)

    Returns:
        Eased value
    """
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t


def ease_in_cubic(t):
    """Cubic ease-in easing function.

    Args:
        t: Progress value (0.0 to 1.0)

    Returns:
        Eased value
    """
    return t * t * t


def ease_out_cubic(t):
    """Cubic ease-out easing function.

    Args:
        t: Progress value (0.0 to 1.0)

    Returns:
        Eased value
    """
    t -= 1
    return t * t * t + 1


def ease_in_out_cubic(t):
    """Cubic ease-in-out easing function.

    Args:
        t: Progress value (0.0 to 1.0)

    Returns:
        Eased value
    """
    if t < 0.5:
        return 4 * t * t * t
    t -= 1
    return 1 + 4 * t * t * t


def ease_out_elastic(t):
    """Elastic ease-out easing function (bounce at end).

    Args:
        t: Progress value (0.0 to 1.0)

    Returns:
        Eased value
    """
    if t == 0:
        return 0
    if t == 1:
        return 1
    return math.pow(2, -10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3) + 1


def ease_out_back(t):
    """Back ease-out easing function (slight overshoot).

    Args:
        t: Progress value (0.0 to 1.0)

    Returns:
        Eased value
    """
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * math.pow(t - 1, 3) + c1 * math.pow(t - 1, 2)


def ease_in_sine(t):
    """Sine ease-in easing function.

    Args:
        t: Progress value (0.0 to 1.0)

    Returns:
        Eased value
    """
    return 1 - math.cos((t * math.pi) / 2)


def ease_out_sine(t):
    """Sine ease-out easing function.

    Args:
        t: Progress value (0.0 to 1.0)

    Returns:
        Eased value
    """
    return math.sin((t * math.pi) / 2)


def pulse(t, frequency=1.0):
    """Create a pulsing sine wave value.

    Args:
        t: Time value
        frequency: Frequency of the pulse

    Returns:
        Value between 0.0 and 1.0
    """
    return (math.sin(t * frequency * math.pi * 2) + 1) / 2
