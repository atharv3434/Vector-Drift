"""Asteroids: drifting, spinning, screen-wrapping, and splitting into smaller
pieces when destroyed (until they're small enough to just disappear)."""
from __future__ import annotations

import math
import random

import pygame

from vectordrift import constants as c
from vectordrift.geometry import wrap_position


class Asteroid:
    def __init__(self, position: pygame.Vector2, velocity: pygame.Vector2, size: int, rng: random.Random | None = None):
        if size not in c.ASTEROID_RADIUS_BY_SIZE:
            raise ValueError(f"Invalid asteroid size tier: {size} (must be 1, 2, or 3)")

        rng = rng or random.Random()
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.size = size
        self.radius = c.ASTEROID_RADIUS_BY_SIZE[size]
        self.rotation = rng.uniform(0, 360)
        self.spin_speed = rng.uniform(*c.ASTEROID_SPIN_RANGE)
        self.shape_offsets = _generate_irregular_shape(rng)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.position = wrap_position(self.position, c.SCREEN_WIDTH, c.SCREEN_HEIGHT)
        self.rotation = (self.rotation + self.spin_speed * dt) % 360

    def get_polygon_points(self) -> list[pygame.Vector2]:
        """World-space points for this asteroid's irregular polygon shape,
        applying its current rotation."""
        points = []
        for angle_offset, radius_fraction in self.shape_offsets:
            angle = math.radians(self.rotation + angle_offset)
            r = self.radius * radius_fraction
            points.append(self.position + pygame.Vector2(math.cos(angle), math.sin(angle)) * r)
        return points

    def split(self, rng: random.Random | None = None) -> list["Asteroid"]:
        """Destroy this asteroid, returning 0-2 smaller asteroids in its place.
        Smallest tier (1) returns an empty list — it's just gone."""
        if self.size <= 1:
            return []

        rng = rng or random.Random()
        new_size = self.size - 1
        speed_min, speed_max = c.ASTEROID_SPEED_RANGE_BY_SIZE[new_size]

        children = []
        for _ in range(c.ASTEROID_SPLIT_COUNT):
            angle = rng.uniform(0, 360)
            speed = rng.uniform(speed_min, speed_max)
            velocity = pygame.Vector2(speed, 0).rotate(angle)
            children.append(Asteroid(self.position, velocity, new_size, rng=rng))
        return children

    @property
    def points_value(self) -> int:
        return c.ASTEROID_POINTS_BY_SIZE[self.size]


def _generate_irregular_shape(rng: random.Random, n_points: int = 10) -> list[tuple[float, float]]:
    """Generate a randomized-but-consistent irregular polygon shape as a list
    of (angle_offset_degrees, radius_fraction) pairs — computed once at
    asteroid creation and reused every frame, so the shape doesn't flicker
    between different random polygons each draw call."""
    offsets = []
    for i in range(n_points):
        angle_offset = (360 / n_points) * i + rng.uniform(-10, 10)
        radius_fraction = rng.uniform(0.75, 1.0)
        offsets.append((angle_offset, radius_fraction))
    return offsets


def spawn_asteroid_at_edge(size: int, rng: random.Random | None = None) -> Asteroid:
    """Spawn a new asteroid at a random point along the screen edge, moving
    inward-ish (used for wave starts)."""
    rng = rng or random.Random()
    edge = rng.choice(["top", "bottom", "left", "right"])

    if edge == "top":
        position = pygame.Vector2(rng.uniform(0, c.SCREEN_WIDTH), 0)
    elif edge == "bottom":
        position = pygame.Vector2(rng.uniform(0, c.SCREEN_WIDTH), c.SCREEN_HEIGHT)
    elif edge == "left":
        position = pygame.Vector2(0, rng.uniform(0, c.SCREEN_HEIGHT))
    else:
        position = pygame.Vector2(c.SCREEN_WIDTH, rng.uniform(0, c.SCREEN_HEIGHT))

    speed_min, speed_max = c.ASTEROID_SPEED_RANGE_BY_SIZE[size]
    speed = rng.uniform(speed_min, speed_max)
    angle = rng.uniform(0, 360)
    velocity = pygame.Vector2(speed, 0).rotate(angle)

    return Asteroid(position, velocity, size, rng=rng)