import pygame
import random

# Welcom to uhhh ReWire's particle system
class Particle:
    def __init__(self, position, color, size_range=(2, 6), speed_range=(40, 120), lifetime_range=(0.3, 0.6)):
        self.position = pygame.Vector2(position)
        self.size = random.uniform(*size_range)
        self.color = color
        self.lifetime = random.uniform(*lifetime_range)
        self.age = 0.0

        angle = random.uniform(0, 360)
        speed = random.uniform(*speed_range)
        direction = pygame.Vector2(1, 0).rotate(angle)
        self.velocity = direction * speed
        
        self.drag = random.uniform(2.0, 4.0)

    def update(self, delta_time):
        self.age += delta_time
        self.position += self.velocity * delta_time
        self.velocity -= self.velocity * self.drag * delta_time

    @property
    def is_alive(self):
        return self.age < self.lifetime

    @property
    def progress(self):
        return min(self.age / self.lifetime, 1.0) if self.lifetime > 0 else 1.0

    def draw(self, display, camera_offset):
        alpha = int(255 * (1.0 - self.progress))
        current_size = max(1, self.size * (1.0 - self.progress * 0.5))

        surf = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
        surf.fill((*self.color, alpha))

        screen_x = self.position.x - camera_offset.x - current_size / 2
        screen_y = self.position.y - camera_offset.y - current_size / 2
        display.blit(surf, (screen_x, screen_y))

# this is a basic explosion particle where a particle is thrown at random direction with random velocity
class ParticleSystem:
    def __init__(self):
        self.particles = []

    # python's **kwargs is used for multiple DYNAMIC params, in other words, optional params
    def emit_burst(self, position, color, count=12, **kwargs):
        for _ in range(count):
            self.particles.append(Particle(position, color, **kwargs))

    def update(self, delta_time):
        for particle in self.particles:
            particle.update(delta_time)
        self.particles = [p for p in self.particles if p.is_alive]

    def draw(self, display, camera_offset):
        for particle in self.particles:
            particle.draw(display, camera_offset)