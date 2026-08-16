"""Bullets fired by the ship: straight-line travel with a lifetime, no screen wrap
(classic arcade feel — a bullet you fire disappears if it travels far enough,
rather than potentially wrapping around and hitting you from behind)."""
from __future__ import annotations

import pygame

from vectordrift import constants as c
from vectordrift.geometry import angle_to_direction


class Bullet:
    def __init__(self, position: pygame.Vector2, angle_degrees: float):
        self.position = pygame.Vector2(position)
        self.velocity = angle_to_direction(angle_degrees) * c.BULLET_SPEED
        self.radius = c.BULLET_RADIUS
        self.seconds_left = c.BULLET_LIFETIME_SECONDS

    @property
    def is_alive(self) -> bool:
        return self.seconds_left > 0

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.seconds_left -= dt