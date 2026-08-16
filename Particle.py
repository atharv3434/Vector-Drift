"""Small particle burst effect for asteroid/ship destruction — purely visual,
no gameplay effect, kept as its own lightweight class rather than overloading
Bullet or Asteroid with a "just for show" mode."""
from __future__ import annotations

import random

import pygame

from vectordrift import constants as c


class Particle:
    def __init__(self, position: pygame.Vector2, velocity: pygame.Vector2):
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.seconds_left = c.PARTICLE_LIFETIME_SECONDS

    @property
    def is_alive(self) -> bool:
        return self.seconds_left > 0

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.seconds_left -= dt


def create_burst(position: pygame.Vector2, count: int, rng: random.Random | None = None) -> list[Particle]:
    rng = rng or random.Random()
    particles = []
    for _ in range(count):
        angle = rng.uniform(0, 360)
        speed = rng.uniform(*c.PARTICLE_SPEED_RANGE)
        velocity = pygame.Vector2(speed, 0).rotate(angle)
        particles.append(Particle(position, velocity))
    return particles