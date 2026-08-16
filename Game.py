"""Core game orchestration: owns all entities, advances the simulation each
frame, and applies the rules (shooting, collisions, splitting, scoring,
lives, wave progression). Deliberately has zero pygame-rendering or
event-polling code in it — see main.py for the loop that drives this with
real input and renders it, and input_state.py for how input is decoupled.
This separation is what makes the whole ruleset testable without a display.
"""
from __future__ import annotations

import random
from enum import Enum, auto

import pygame

from vectordrift import constants as c
from vectordrift.asteroid import Asteroid, spawn_asteroid_at_edge
from vectordrift.bullet import Bullet
from vectordrift.geometry import circles_collide
from vectordrift.input_state import InputState
from vectordrift.particle import create_burst
from vectordrift.ship import Ship


class GameState(Enum):
    PLAYING = auto()
    GAME_OVER = auto()


class Game:
    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.ship: Ship = Ship(self._screen_center())
        self.bullets: list[Bullet] = []
        self.asteroids: list[Asteroid] = []
        self.particles: list = []
        self.score = 0
        self.lives = c.STARTING_LIVES
        self.level = 1
        self.state = GameState.PLAYING
        self._bullet_cooldown_remaining = 0.0

        self._spawn_wave(self.level)

    @staticmethod
    def _screen_center() -> pygame.Vector2:
        return pygame.Vector2(c.SCREEN_WIDTH / 2, c.SCREEN_HEIGHT / 2)

    def reset(self) -> None:
        """Full game reset, e.g. after game over + player presses restart."""
        self.ship.reset(self._screen_center())
        self.bullets.clear()
        self.asteroids.clear()
        self.particles.clear()
        self.score = 0
        self.lives = c.STARTING_LIVES
        self.level = 1
        self.state = GameState.PLAYING
        self._bullet_cooldown_remaining = 0.0
        self._spawn_wave(self.level)

    def _spawn_wave(self, level: int) -> None:
        n_asteroids = c.STARTING_ASTEROIDS + c.ASTEROID_INCREMENT_PER_LEVEL * (level - 1)
        for _ in range(n_asteroids):
            asteroid = spawn_asteroid_at_edge(size=3, rng=self.rng)
            self.asteroids.append(asteroid)

    def update(self, dt: float, input_state: InputState) -> None:
        if self.state == GameState.GAME_OVER:
            return

        self.ship.update(dt, thrust_input=input_state.thrust, rotate_input=input_state.rotate_direction)

        self._bullet_cooldown_remaining = max(0.0, self._bullet_cooldown_remaining - dt)
        if input_state.shoot and self._bullet_cooldown_remaining <= 0:
            self._fire_bullet()

        for bullet in self.bullets:
            bullet.update(dt)
        self.bullets = [b for b in self.bullets if b.is_alive]

        for asteroid in self.asteroids:
            asteroid.update(dt)

        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.is_alive]

        self._handle_bullet_asteroid_collisions()
        self._handle_ship_asteroid_collisions()

        if not self.asteroids:
            self.level += 1
            self._spawn_wave(self.level)

    def _fire_bullet(self) -> None:
        bullet = Bullet(self.ship.get_nose_position(), self.ship.angle)
        self.bullets.append(bullet)
        self._bullet_cooldown_remaining = c.BULLET_COOLDOWN_SECONDS

    def _handle_bullet_asteroid_collisions(self) -> None:
        surviving_bullets = []
        for bullet in self.bullets:
            hit_asteroid = None
            for asteroid in self.asteroids:
                if circles_collide(bullet.position, bullet.radius, asteroid.position, asteroid.radius):
                    hit_asteroid = asteroid
                    break  # a bullet can only hit one asteroid per frame

            if hit_asteroid is None:
                surviving_bullets.append(bullet)
                continue

            self._destroy_asteroid(hit_asteroid)

        self.bullets = surviving_bullets

    def _destroy_asteroid(self, asteroid: Asteroid) -> None:
        self.score += asteroid.points_value
        self.particles.extend(create_burst(asteroid.position, c.PARTICLE_COUNT_PER_ASTEROID, rng=self.rng))
        self.asteroids.remove(asteroid)
        self.asteroids.extend(asteroid.split(rng=self.rng))

    def _handle_ship_asteroid_collisions(self) -> None:
        if self.ship.is_invulnerable:
            return

        for asteroid in self.asteroids:
            if circles_collide(self.ship.position, self.ship.radius, asteroid.position, asteroid.radius):
                self._destroy_ship()
                return  # only one hit can happen per frame; ship is now respawning/invulnerable or game over

    def _destroy_ship(self) -> None:
        self.particles.extend(create_burst(self.ship.position, c.PARTICLE_COUNT_PER_ASTEROID, rng=self.rng))
        self.lives -= 1
        if self.lives <= 0:
            self.state = GameState.GAME_OVER
        else:
            self.ship.reset(self._screen_center())