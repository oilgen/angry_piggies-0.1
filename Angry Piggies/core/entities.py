"""Игровые сущности."""

from kivy.graphics import Color, Ellipse, Rectangle, Line


class Block:
    def __init__(self, x, y, w, h, material="wood", hp=100):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.material = material
        self.max_hp = hp
        self.hp = hp
        self.alive = True

        self.vy = 0.0
        self.grounded = y <= 70
        self.tilt = 0.0

        self.colors = {
            "wood":  (0.65, 0.42, 0.18),
            "stone": (0.50, 0.50, 0.55),
            "ice":   (0.70, 0.90, 1.00),
        }

    def rect(self):
        return (self.x, self.y, self.w, self.h)

    def supports(self, other):
        """True, если этот блок стоит на other."""
        return (
            abs(self.y - (other.y + other.h)) < 8
            and self.x + self.w > other.x + 4
            and self.x < other.x + other.w - 4
        )

    def draw(self, canvas):
        if not self.alive:
            return
        base = self.colors.get(self.material, (0.5, 0.5, 0.5))
        damage = 1 - (self.hp / self.max_hp)
        shade = 1 - damage * 0.55
        canvas.add(Color(base[0] * shade, base[1] * shade, base[2] * shade))
        dx = self.tilt * 20
        canvas.add(Rectangle(pos=(self.x + dx, self.y), size=(self.w, self.h)))
        canvas.add(Color(0.15, 0.1, 0.05))
        canvas.add(Line(rectangle=(self.x + dx, self.y, self.w, self.h), width=1.5))

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True
        return False


class Bird:
    def __init__(self, x, y, w=40, h=40, hp=50):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.max_hp = hp
        self.hp = hp
        self.alive = True
        self.vy = 0.0
        self.grounded = False
        self.fall_start_y = y

    def rect(self):
        # Хитбокс делаем на 10 пикселей больше с каждой стороны, 
        # чтобы свинья не пролетала сквозь птицу на огромной скорости.
        pad = 10
        return (self.x - pad, self.y - pad, self.w + pad * 2, self.h + pad * 2)

    def draw(self, canvas):
        if not self.alive:
            return
        cx, cy = self.x + self.w / 2, self.y + self.h / 2
        canvas.add(Color(1.0, 0.85, 0.2))
        canvas.add(Ellipse(pos=(cx - self.w / 2, cy - self.h / 2),
                           size=(self.w, self.h)))
        canvas.add(Color(1, 1, 1))
        canvas.add(Ellipse(pos=(cx - 8, cy + 4), size=(9, 9)))
        canvas.add(Ellipse(pos=(cx + 2, cy + 4), size=(9, 9)))
        canvas.add(Color(0, 0, 0))
        canvas.add(Ellipse(pos=(cx - 5, cy + 7), size=(5, 5)))
        canvas.add(Ellipse(pos=(cx + 5, cy + 7), size=(5, 5)))
        canvas.add(Color(1.0, 0.5, 0.0))
        canvas.add(Ellipse(pos=(cx + 10, cy - 6), size=(12, 9)))

    def hit(self, damage):
        if not self.alive:
            return False
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            return True
        return False


class Pig:
    def __init__(self, x, y, w=30, h=30):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.vx = 0.0
        self.vy = 0.0
        self.stopped = False
        self.trail = []

    def rect(self):
        return (self.x, self.y, self.w, self.h)

    def draw(self, canvas):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = i / max(len(self.trail), 1)
            canvas.add(Color(0.2, 0.7, 0.2, alpha * 0.4))
            r = 5 * (1 - alpha * 0.5)
            canvas.add(Ellipse(pos=(tx - r, ty - r), size=(r * 2, r * 2)))

        cx, cy = self.x + self.w / 2, self.y + self.h / 2
        canvas.add(Color(0.3, 0.75, 0.3))
        canvas.add(Ellipse(pos=(cx - self.w / 2, cy - self.h / 2),
                           size=(self.w, self.h)))
        canvas.add(Color(0.2, 0.6, 0.2))
        canvas.add(Ellipse(pos=(cx - 6, cy - 4), size=(12, 8)))
        canvas.add(Color(1, 1, 1))
        canvas.add(Ellipse(pos=(cx - 9, cy + 4), size=(7, 7)))
        canvas.add(Ellipse(pos=(cx + 2, cy + 4), size=(7, 7)))
        canvas.add(Color(0, 0, 0))
        canvas.add(Ellipse(pos=(cx - 6, cy + 6), size=(4, 4)))
        canvas.add(Ellipse(pos=(cx + 5, cy + 6), size=(4, 4)))