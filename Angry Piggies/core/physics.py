"""Физика для игры Angry Piggies."""

GRAVITY = 1400.0
BLOCK_GRAVITY = 1800.0
FIXED_DT = 1.0 / 60.0


def aabb_collide(r1, r2):
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    return (
        x1 < x2 + w2
        and x1 + w1 > x2
        and y1 < y2 + h2
        and y1 + h1 > y2
    )