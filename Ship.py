"""The player ship: rotation, thrust-based inertial movement, screen wrap."""
from __future__ import annotations

import pygame

from vectordrift import constants as c
from vectordrift.geometry import angle_to_direction, wrap_position


class Ship:
    def __init__(self, position: pygame.Vector2):
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(0, 0)
        self.angle = 0.0  # degrees, 0 = up, clockwise-increasing
        self.radius = c.SHIP_RADIUS
        self.is_thrusting = False
        self.invulnerable_seconds_left = c.SHIP_INVULNERABILITY_SECONDS

    @property
    def is_invulnerable(self) -> bool:
        return self.invulnerable_seconds_left > 0

    def rotate(self, direction: int, dt: float) -> None:
        """@param direction -1 for left, +1 for right, 0 for no input."""
        self.angle = (self.angle + direction * c.SHIP_ROTATION_SPEED * dt) % 360

    def apply_thrust(self, dt: float) -> None:
        forward = angle_to_direction(self.angle)
        self.velocity += forward * c.SHIP_THRUST_ACCEL * dt
        if self.velocity.length() > c.SHIP_MAX_SPEED:
            self.velocity.scale_to_length(c.SHIP_MAX_SPEED)

    def update(self, dt: float, thrust_input: bool, rotate_input: int) -> None:
        self.is_thrusting = thrust_input
        self.rotate(rotate_input, dt)
        if thrust_input:
            self.apply_thrust(dt)

        # Mild drag makes the ship feel controllable rather than purely
        # Newtonian-frictionless, which (per genuine Asteroids-clone design
        # experience) is more fun for most players even though it's not
        # physically accurate for a ship in a vacuum.
        drag_factor = max(0.0, 1.0 - c.SHIP_DRAG * dt)
        self.velocity *= drag_factor

        self.position += self.velocity * dt
        self.position = wrap_position(self.position, c.SCREEN_WIDTH, c.SCREEN_HEIGHT)

        if self.invulnerable_seconds_left > 0:
            self.invulnerable_seconds_left = max(0.0, self.invulnerable_seconds_left - dt)

    def get_nose_position(self) -> pygame.Vector2:
        """Where bullets spawn from — the tip of the ship's triangle."""
        return self.position + angle_to_direction(self.angle) * self.radius

    def get_triangle_points(self) -> list[pygame.Vector2]:
        """Three points defining the ship's triangle in world space, for rendering."""
        forward = angle_to_direction(self.angle)
        right = pygame.Vector2(-forward.y, forward.x)  # perpendicular to forward

        nose = self.position + forward * self.radius
        left_wing = self.position - forward * self.radius * 0.7 + right * self.radius * 0.7
        right_wing = self.position - forward * self.radius * 0.7 - right * self.radius * 0.7
        return [nose, left_wing, right_wing]

    def reset(self, position: pygame.Vector2) -> None:
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(0, 0)
        self.angle = 0.0
        self.invulnerable_seconds_left = c.SHIP_INVULNERABILITY_SECONDS