"""Pure geometry helpers with no rendering dependency — these are the parts
of the game most worth unit testing directly, since a subtle bug here (e.g.
wrapping math off by one, or collision radius using diameter instead of
radius) would be a real, easy-to-make mistake that's otherwise only visible
by eyeballing gameplay.
"""
from __future__ import annotations

import math

import pygame


def wrap_position(position: pygame.Vector2, width: int, height: int) -> pygame.Vector2:
    """Wrap a position around screen edges (Asteroids-style toroidal space).
    Returns a new Vector2 rather than mutating in place, to keep this
    function easy to reason about and test in isolation.
    """
    x = position.x % width
    y = position.y % height
    return pygame.Vector2(x, y)


def circles_collide(pos_a: pygame.Vector2, radius_a: float, pos_b: pygame.Vector2, radius_b: float) -> bool:
    """Simple circle-circle collision test. All game entities use circular
    collision bounds (even though asteroids render as irregular polygons) —
    a deliberate simplification that keeps collision math fast and testable,
    at the cost of being slightly generous near an asteroid's polygon points.
    """
    distance_squared = (pos_a.x - pos_b.x) ** 2 + (pos_a.y - pos_b.y) ** 2
    radius_sum = radius_a + radius_b
    return distance_squared <= radius_sum * radius_sum


def angle_to_direction(angle_degrees: float) -> pygame.Vector2:
    """Convert a heading angle (0 = up, increasing clockwise, matching how
    the ship's nose is drawn) into a unit direction vector."""
    radians = math.radians(angle_degrees - 90)
    return pygame.Vector2(math.cos(radians), math.sin(radians))