"""Rendering: draws the current game state to a pygame Surface. Kept
completely separate from Game's logic — this module never mutates game
state, only reads it, which is what let Game itself be tested with zero
pygame-display dependency.
"""
from __future__ import annotations

import pygame

from vectordrift import constants as c
from vectordrift.game import Game, GameState
from vectordrift.geometry import angle_to_direction

_font_cache: dict[int, pygame.font.Font] = {}


def _get_font(size: int) -> pygame.font.Font:
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont("couriernew,monospace", size, bold=True)
    return _font_cache[size]


def draw(surface: pygame.Surface, game: Game) -> None:
    surface.fill(c.COLOR_BACKGROUND)

    for asteroid in game.asteroids:
        pygame.draw.polygon(surface, c.COLOR_ASTEROID, asteroid.get_polygon_points(), width=2)

    for bullet in game.bullets:
        pygame.draw.circle(surface, c.COLOR_BULLET, bullet.position, bullet.radius)

    for particle in game.particles:
        alpha_fraction = max(0.0, particle.seconds_left / c.PARTICLE_LIFETIME_SECONDS)
        radius = max(1, int(2 * alpha_fraction))
        pygame.draw.circle(surface, c.COLOR_PARTICLE, particle.position, radius)

    _draw_ship(surface, game)
    _draw_hud(surface, game)

    if game.state == GameState.GAME_OVER:
        _draw_game_over(surface, game)


def _draw_ship(surface: pygame.Surface, game: Game) -> None:
    ship = game.ship
    if ship.is_invulnerable:
        # Blink during invulnerability so the player can see they're safe,
        # without the ship fully disappearing (which reads as a bug, not a feature).
        blink_phase = (c.SHIP_INVULNERABILITY_SECONDS - ship.invulnerable_seconds_left) * c.SHIP_RESPAWN_BLINK_HZ
        if int(blink_phase) % 2 == 1:
            return

    pygame.draw.polygon(surface, c.COLOR_SHIP, ship.get_triangle_points(), width=2)

    if ship.is_thrusting:
        _draw_thrust_flame(surface, ship)


def _draw_thrust_flame(surface: pygame.Surface, ship) -> None:
    forward = angle_to_direction(ship.angle)
    right = pygame.Vector2(-forward.y, forward.x)

    flame_tip = ship.position - forward * ship.radius * 1.6
    flame_left = ship.position - forward * ship.radius * 0.6 + right * ship.radius * 0.35
    flame_right = ship.position - forward * ship.radius * 0.6 - right * ship.radius * 0.35

    pygame.draw.polygon(surface, c.COLOR_SHIP_THRUST, [flame_tip, flame_left, flame_right])


def _draw_hud(surface: pygame.Surface, game: Game) -> None:
    font = _get_font(22)
    score_surf = font.render(f"SCORE {game.score:06d}", True, c.COLOR_TEXT)
    surface.blit(score_surf, (16, 14))

    level_surf = font.render(f"WAVE {game.level}", True, c.COLOR_TEXT_DIM)
    surface.blit(level_surf, (16, 42))

    lives_label = font.render("LIVES", True, c.COLOR_TEXT_DIM)
    surface.blit(lives_label, (c.SCREEN_WIDTH - 160, 14))
    for i in range(max(0, game.lives)):
        _draw_life_icon(surface, c.SCREEN_WIDTH - 60 + i * 26, 24)


def _draw_life_icon(surface: pygame.Surface, x: int, y: int) -> None:
    points = [
        pygame.Vector2(x, y - 9),
        pygame.Vector2(x - 7, y + 7),
        pygame.Vector2(x + 7, y + 7),
    ]
    pygame.draw.polygon(surface, c.COLOR_SHIP, points, width=2)


def _draw_game_over(surface: pygame.Surface, game: Game) -> None:
    overlay = pygame.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surface.blit(overlay, (0, 0))

    big_font = _get_font(48)
    small_font = _get_font(20)

    title = big_font.render("GAME OVER", True, c.COLOR_GAME_OVER)
    title_rect = title.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 - 40))
    surface.blit(title, title_rect)

    score_text = small_font.render(f"Final score: {game.score}", True, c.COLOR_TEXT)
    score_rect = score_text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + 10))
    surface.blit(score_text, score_rect)

    hint_text = small_font.render("Press R to restart", True, c.COLOR_TEXT_DIM)
    hint_rect = hint_text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + 42))
    surface.blit(hint_text, hint_rect)