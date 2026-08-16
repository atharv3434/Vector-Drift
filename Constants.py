"""Central tuning constants for Vector Drift. Keeping every magic number here
makes the game's feel easy to iterate on without hunting through logic code."""

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 60

# --- Colors ---
COLOR_BACKGROUND = (8, 10, 20)
COLOR_SHIP = (235, 240, 255)
COLOR_SHIP_THRUST = (255, 170, 60)
COLOR_BULLET = (255, 230, 120)
COLOR_ASTEROID = (150, 165, 200)
COLOR_TEXT = (235, 240, 255)
COLOR_TEXT_DIM = (140, 150, 175)
COLOR_GAME_OVER = (255, 90, 90)
COLOR_PARTICLE = (255, 200, 120)

# --- Ship physics ---
SHIP_RADIUS = 14
SHIP_ROTATION_SPEED = 220.0  # degrees per second
SHIP_THRUST_ACCEL = 260.0  # pixels/sec^2
SHIP_MAX_SPEED = 340.0
SHIP_DRAG = 0.35  # fraction of velocity lost per second (space has no drag physically, but a little makes it more fun to control)
SHIP_INVULNERABILITY_SECONDS = 2.5
SHIP_RESPAWN_BLINK_HZ = 6.0

# --- Bullets ---
BULLET_SPEED = 480.0
BULLET_RADIUS = 2.5
BULLET_LIFETIME_SECONDS = 1.1
BULLET_COOLDOWN_SECONDS = 0.22

# --- Asteroids ---
# size tiers: 3 = large, 2 = medium, 1 = small
ASTEROID_RADIUS_BY_SIZE = {3: 46, 2: 26, 1: 14}
ASTEROID_POINTS_BY_SIZE = {3: 20, 2: 50, 1: 100}  # smaller = harder to hit = worth more, classic arcade convention
ASTEROID_SPEED_RANGE_BY_SIZE = {
    3: (30.0, 70.0),
    2: (55.0, 110.0),
    1: (90.0, 160.0),
}
ASTEROID_SPLIT_COUNT = 2
ASTEROID_SPIN_RANGE = (-60.0, 60.0)  # degrees/sec, visual only

# --- Waves / lives ---
STARTING_LIVES = 3
STARTING_ASTEROIDS = 4
ASTEROID_INCREMENT_PER_LEVEL = 2
SHIP_SAFE_SPAWN_RADIUS = 140  # asteroids won't spawn within this distance of screen center on wave start

# --- Particles (destruction effect) ---
PARTICLE_COUNT_PER_ASTEROID = 8
PARTICLE_SPEED_RANGE = (40.0, 140.0)
PARTICLE_LIFETIME_SECONDS = 0.5