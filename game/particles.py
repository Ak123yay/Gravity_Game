"""Particle system for visual effects."""

import pygame
import random
import math


class Particle:
    """Individual particle with position, velocity, and lifetime."""

    def __init__(self, x, y, vx, vy, color, size, lifetime, gravity=None):
        """Initialize particle.

        Args:
            x: X position
            y: Y position
            vx: X velocity
            vy: Y velocity
            color: RGB color tuple
            size: Particle size in pixels
            lifetime: Total lifetime in seconds
            gravity: Optional (gx, gy) gravity vector
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity if gravity else (0, 0)
        self.alpha = 255

    def update(self, dt):
        """Update particle position and lifetime.

        Args:
            dt: Delta time in seconds

        Returns:
            True if particle is still alive, False if expired
        """
        # Apply gravity
        self.vx += self.gravity[0] * dt
        self.vy += self.gravity[1] * dt

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Decrement lifetime
        self.lifetime -= dt

        # Update alpha based on lifetime
        life_ratio = self.lifetime / self.max_lifetime
        self.alpha = int(255 * life_ratio)

        return self.lifetime > 0

    def draw(self, screen, camera_offset=(0, 0)):
        """Draw particle to screen.

        Args:
            screen: pygame.Surface to draw on
            camera_offset: (x, y) camera offset for screen shake
        """
        if self.alpha > 0:
            x = int(self.x + camera_offset[0])
            y = int(self.y + camera_offset[1])
            size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))

            # Create surface with alpha
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(surf, color_with_alpha, (size, size), size)

            # Blit to screen
            screen.blit(surf, (x - size, y - size))


class ParticleEmitter:
    """Manages and emits particles."""

    def __init__(self, max_particles=100):
        """Initialize particle emitter.

        Args:
            max_particles: Maximum number of active particles
        """
        self.particles = []
        self.max_particles = max_particles

    def emit_burst(self, x, y, count, color, speed_range=(50, 150), size_range=(2, 5), lifetime_range=(0.3, 0.8), gravity=None):
        """Emit a burst of particles in all directions.

        Args:
            x: Center X position
            y: Center Y position
            count: Number of particles to emit
            color: RGB color tuple or list of colors
            speed_range: (min, max) speed in pixels/second
            size_range: (min, max) particle size
            lifetime_range: (min, max) lifetime in seconds
            gravity: Optional (gx, gy) gravity vector
        """
        for _ in range(count):
            # Random direction
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            # Random properties
            particle_color = random.choice(color) if isinstance(color[0], (list, tuple)) else color
            size = random.uniform(*size_range)
            lifetime = random.uniform(*lifetime_range)

            # Add slight position variation
            px = x + random.uniform(-5, 5)
            py = y + random.uniform(-5, 5)

            self._add_particle(Particle(px, py, vx, vy, particle_color, size, lifetime, gravity))

    def emit_trail(self, x, y, color, vx=0, vy=0, size=3, lifetime=0.5):
        """Emit a single trail particle.

        Args:
            x: X position
            y: Y position
            color: RGB color tuple
            vx: X velocity
            vy: Y velocity
            size: Particle size
            lifetime: Particle lifetime
        """
        # Add small random variation
        px = x + random.uniform(-2, 2)
        py = y + random.uniform(-2, 2)
        pvx = vx + random.uniform(-10, 10)
        pvy = vy + random.uniform(-10, 10)

        self._add_particle(Particle(px, py, pvx, pvy, color, size, lifetime, gravity=(0, 50)))

    def emit_confetti(self, x, y, count, colors):
        """Emit confetti particles that fall from top.

        Args:
            x: Center X position
            y: Top Y position
            count: Number of particles
            colors: List of RGB color tuples
        """
        for _ in range(count):
            px = x + random.uniform(-200, 200)
            py = y + random.uniform(-50, 50)
            vx = random.uniform(-80, 80)
            vy = random.uniform(20, 80)
            color = random.choice(colors)
            size = random.uniform(3, 7)
            lifetime = random.uniform(2.0, 4.0)

            self._add_particle(Particle(px, py, vx, vy, color, size, lifetime, gravity=(0, 200)))

    def emit_ambient(self, x, y, width, height, count, color, speed=20):
        """Emit ambient floating particles.

        Args:
            x: Area X position
            y: Area Y position
            width: Area width
            height: Area height
            count: Number of particles
            color: RGB color tuple
            speed: Particle speed
        """
        for _ in range(count):
            px = random.uniform(x, x + width)
            py = random.uniform(y, y + height)
            angle = random.uniform(0, math.pi * 2)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(1, 3)
            lifetime = random.uniform(2.0, 5.0)

            self._add_particle(Particle(px, py, vx, vy, color, size, lifetime))

    def emit_directional(self, x, y, direction, count, color, speed_range=(50, 150), spread=0.5):
        """Emit particles in a specific direction.

        Args:
            x: Center X position
            y: Center Y position
            direction: Direction in radians (0 = right, pi/2 = down)
            count: Number of particles
            color: RGB color tuple
            speed_range: (min, max) speed in pixels/second
            spread: Angle spread in radians
        """
        for _ in range(count):
            angle = direction + random.uniform(-spread, spread)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(2, 5)
            lifetime = random.uniform(0.3, 0.8)

            px = x + random.uniform(-3, 3)
            py = y + random.uniform(-3, 3)

            self._add_particle(Particle(px, py, vx, vy, color, size, lifetime))

    def _add_particle(self, particle):
        """Add a particle to the system.

        Args:
            particle: Particle instance
        """
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)

    def update(self, dt):
        """Update all particles.

        Args:
            dt: Delta time in seconds
        """
        # Update particles and remove dead ones
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, screen, camera_offset=(0, 0)):
        """Draw all particles.

        Args:
            screen: pygame.Surface to draw on
            camera_offset: (x, y) camera offset for screen shake
        """
        for particle in self.particles:
            particle.draw(screen, camera_offset)

    def clear(self):
        """Remove all particles."""
        self.particles.clear()

    def get_count(self):
        """Get number of active particles.

        Returns:
            Number of active particles
        """
        return len(self.particles)


class ParticleManager:
    """Manages multiple particle emitters for different purposes."""

    def __init__(self, max_particles=100):
        """Initialize particle manager.

        Args:
            max_particles: Maximum total particles across all emitters
        """
        self.max_particles = max_particles
        self.emitters = {
            'gameplay': ParticleEmitter(max_particles // 2),
            'ui': ParticleEmitter(max_particles // 4),
            'ambient': ParticleEmitter(max_particles // 4)
        }

    def emit(self, emitter_name, emit_type, **kwargs):
        """Emit particles from a specific emitter.

        Args:
            emitter_name: Name of emitter ('gameplay', 'ui', 'ambient')
            emit_type: Type of emission ('burst', 'trail', 'confetti', 'ambient', 'directional')
            **kwargs: Parameters for the emission type
        """
        if emitter_name not in self.emitters:
            return

        emitter = self.emitters[emitter_name]

        if emit_type == 'burst':
            emitter.emit_burst(**kwargs)
        elif emit_type == 'trail':
            emitter.emit_trail(**kwargs)
        elif emit_type == 'confetti':
            emitter.emit_confetti(**kwargs)
        elif emit_type == 'ambient':
            emitter.emit_ambient(**kwargs)
        elif emit_type == 'directional':
            emitter.emit_directional(**kwargs)

    def update(self, dt):
        """Update all emitters.

        Args:
            dt: Delta time in seconds
        """
        for emitter in self.emitters.values():
            emitter.update(dt)

    def draw(self, screen, camera_offset=(0, 0)):
        """Draw all particles from all emitters.

        Args:
            screen: pygame.Surface to draw on
            camera_offset: (x, y) camera offset
        """
        # Draw in order: ambient, gameplay, ui
        for name in ['ambient', 'gameplay', 'ui']:
            self.emitters[name].draw(screen, camera_offset)

    def clear_all(self):
        """Clear all particles from all emitters."""
        for emitter in self.emitters.values():
            emitter.clear()

    def get_total_count(self):
        """Get total number of active particles.

        Returns:
            Total particle count
        """
        return sum(e.get_count() for e in self.emitters.values())
