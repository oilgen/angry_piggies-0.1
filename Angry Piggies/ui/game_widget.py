"""Игровое поле: физика, отрисовка, взаимодействие."""

import math

from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.clock import Clock

from core.entities import Pig, Bird, Block
from core.physics import GRAVITY, BLOCK_GRAVITY, FIXED_DT, aabb_collide


class GameWidget(Widget):
    def __init__(self, level_data, entities_data, on_win, on_lose, **kwargs):
        super().__init__(**kwargs)
        self.level_data = level_data
        self.on_win = on_win
        self.on_lose = on_lose

        self.slingshot_x = 120
        self.slingshot_y = 130
        self.ground_y = 70

        self.blocks = []
        self.birds = []
        self._load_level(entities_data)

        self.pigs_remaining = level_data["num_pigs"]
        self.flying_pigs = []

        self.dragging = False
        self.drag_pos = None
        self.max_drag = 150
        self.power = 9.0

        self.game_status = "aiming"
        self.accumulator = 0.0

        Clock.schedule_interval(self._on_tick, FIXED_DT)

    def _load_level(self, entities_data):
        for e in entities_data:
            if e["entity_type"] == "block":
                self.blocks.append(Block(
                    e["x"], e["y"], e["width"], e["height"],
                    material=e["material"] or "wood",
                    hp=e["hp"] or 100,
                ))
            elif e["entity_type"] == "bird":
                self.birds.append(Bird(
                    e["x"], e["y"], e["width"] or 40, e["height"] or 40,
                    hp=e["hp"] or 50,
                ))

    # ---------- Ввод ----------

    def on_touch_down(self, touch):
        if self.game_status != "aiming":
            return super().on_touch_down(touch)
        dx = touch.x - self.slingshot_x
        dy = touch.y - self.slingshot_y
        if dx * dx + dy * dy < 90 * 90 and self.pigs_remaining > 0:
            self.dragging = True
            self.drag_pos = (touch.x, touch.y)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.dragging:
            self.drag_pos = (touch.x, touch.y)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.dragging:
            self.dragging = False
            dx = self.slingshot_x - self.drag_pos[0]
            dy = self.slingshot_y - self.drag_pos[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > self.max_drag:
                dx = dx / dist * self.max_drag
                dy = dy / dist * self.max_drag
            if dist > 20:
                self._launch_pig(dx * self.power, dy * self.power)
            self.drag_pos = None
            return True
        return super().on_touch_up(touch)

    def _launch_pig(self, vx, vy):
        pig = Pig(self.slingshot_x - 15, self.slingshot_y - 15)
        pig.vx = vx
        pig.vy = vy
        self.flying_pigs.append(pig)
        self.pigs_remaining -= 1
        self.game_status = "flying"

    # ---------- Тик ----------

    def _on_tick(self, dt):
        self.accumulator += dt
        while self.accumulator >= FIXED_DT:
            self._step(FIXED_DT)
            self.accumulator -= FIXED_DT
        self._draw()

    def _step(self, dt):
        self._update_pigs(dt)
        self._update_stability(dt)
        self._update_blocks(dt)
        self._update_birds(dt)
        self._check_end_turn()

    # ---------- Свины ----------

    def _update_pigs(self, dt):
        for pig in self.flying_pigs:
            if pig.stopped:
                continue

            pig.vy -= GRAVITY * dt
            pig.x += pig.vx * dt
            pig.y += pig.vy * dt

            pig.trail.append((pig.x + pig.w / 2, pig.y + pig.h / 2))
            if len(pig.trail) > 20:
                pig.trail.pop(0)

            if pig.y < self.ground_y:
                pig.y = self.ground_y
                pig.stopped = True
                pig.vx = pig.vy = 0
                continue
            if pig.x > self.width + 100 or pig.x < -100:
                pig.stopped = True
                continue

            pig_rect = pig.rect()

            # 1. Птицы — мгновенное убийство
            bird_hit = False
            for bird in self.birds:
                if not bird.alive:
                    continue
                if aabb_collide(pig_rect, bird.rect()):
                    bird.hit(999)
                    bird_hit = True
                    break

            if bird_hit:
                pig.stopped = True
                pig.vx = pig.vy = 0
                continue

            # 2. Блоки — урон 100
            for block in self.blocks:
                if not block.alive:
                    continue
                if aabb_collide(pig_rect, block.rect()):
                    destroyed = block.hit(100)
                    pig.stopped = True
                    pig.vx = pig.vy = 0
                    if destroyed:
                        self._wake_neighbours(block, radius=100, damage=40)
                    else:
                        self._wake_neighbours(block, radius=60, damage=10)
                    break

    def _wake_neighbours(self, block, radius, damage):
        for other in self.blocks:
            if other is block or not other.alive:
                continue
            dx = abs((other.x + other.w / 2) - (block.x + block.w / 2))
            dy = abs((other.y + other.h / 2) - (block.y + block.h / 2))
            if dx < radius and dy < radius:
                other.hit(damage)

    # ---------- Устойчивость конструкций ----------

    def _update_stability(self, dt):
        """Проверяем опоры. Горизонтальные перекладины падают, если
        у них осталась только одна вертикальная опора."""
        for block in self.blocks:
            if not block.alive:
                continue

            # Блок на земле — устойчив
            if block.y <= self.ground_y + 2:
                block.grounded = True
                block.tilt = 0.0
                continue

            # Ищем опоры под блоком
            left_support = False
            right_support = False
            any_support = False

            for other in self.blocks:
                if other is block or not other.alive:
                    continue
                if block.supports(other):
                    any_support = True
                    center_other = other.x + other.w / 2
                    center_block = block.x + block.w / 2
                    if center_other < center_block - 5:
                        left_support = True
                    elif center_other > center_block + 5:
                        right_support = True
                    else:
                        left_support = True
                        right_support = True

            is_horizontal = block.w > block.h * 2

            if is_horizontal:
                # Перекладина: нужны ОБЕ опоры (левая и правая)
                if left_support and right_support:
                    block.grounded = True
                    block.tilt = 0.0
                elif left_support or right_support:
                    # Одна опора — перекладина кренится и падает
                    block.grounded = False
                    block.tilt = min(1.0, block.tilt + 0.1)
                else:
                    block.grounded = False
            else:
                # Вертикальный блок — достаточно любой опоры
                if any_support:
                    block.grounded = True
                else:
                    block.grounded = False

    # ---------- Блоки ----------

    def _update_blocks(self, dt):
        for block in self.blocks:
            if not block.alive or block.grounded:
                continue

            block.vy -= BLOCK_GRAVITY * dt
            block.y += block.vy * dt

            if block.y <= self.ground_y:
                block.y = self.ground_y
                block.vy = 0
                block.grounded = True
                continue

            for other in self.blocks:
                if other is block or not other.alive:
                    continue
                if aabb_collide(block.rect(), other.rect()):
                    if block.vy < 0:
                        impact = abs(block.vy)
                        block.y = other.y + other.h
                        block.vy = 0
                        block.grounded = True
                        other.hit(impact / 10)
                    break

            for bird in self.birds:
                if not bird.alive:
                    continue
                if aabb_collide(block.rect(), bird.rect()):
                    bird.hit(999)
                    block.vy = 0
                    block.grounded = True
                    break

    # ---------- Птицы ----------

    def _update_birds(self, dt):
        for bird in self.birds:
            if not bird.alive:
                continue

            # Птица на земле
            if bird.y <= self.ground_y + 1:
                bird.y = self.ground_y
                bird.grounded = True
                bird.vy = 0
                continue

            # Проверяем, есть ли опора под птицей
            has_support = False
            for block in self.blocks:
                if not block.alive:
                    continue
                # Птица стоит на блоке, если низ птицы совпадает с верхом блока
                if (abs(bird.y - (block.y + block.h)) < 8
                        and bird.x + bird.w > block.x + 4
                        and bird.x < block.x + block.w - 4):
                    has_support = True
                    break

            if has_support:
                bird.grounded = True
                bird.vy = 0
                continue

            # Опора пропала — птица падает
            bird.grounded = False
            if bird.vy == 0:
                bird.fall_start_y = bird.y
            bird.vy -= GRAVITY * dt
            bird.y += bird.vy * dt

            # Урон от падения
            if bird.y <= self.ground_y:
                fall_distance = bird.fall_start_y - bird.y
                if fall_distance > 30:
                    bird.hit(fall_distance / 2)
                bird.y = self.ground_y
                bird.vy = 0
                bird.grounded = True

    # ---------- Конец хода ----------

    def _check_end_turn(self):
        if self.game_status != "flying":
            return

        all_pigs_stopped = all(p.stopped for p in self.flying_pigs)
        all_blocks_settled = all(b.grounded or not b.alive for b in self.blocks)
        all_birds_settled = all(b.grounded or not b.alive for b in self.birds)

        if all_pigs_stopped and all_blocks_settled and all_birds_settled:
            if all(not b.alive for b in self.birds):
                self.game_status = "won"
                stars = self._calculate_stars()
                Clock.schedule_once(lambda *_: self.on_win(stars), 0.4)
            elif self.pigs_remaining <= 0:
                self.game_status = "lost"
                Clock.schedule_once(lambda *_: self.on_lose(), 0.4)
            else:
                self.game_status = "aiming"
                self.flying_pigs.clear()

    def _calculate_stars(self):
        if self.pigs_remaining >= 2:
            return 3
        if self.pigs_remaining == 1:
            return 2
        return 1

    # ---------- Отрисовка ----------

    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.53, 0.81, 0.92)
            Rectangle(pos=(0, 0), size=(self.width, self.height))

            Color(1.0, 0.9, 0.3)
            Ellipse(pos=(self.width - 140, self.height - 120), size=(80, 80))

            Color(1, 1, 1)
            for cx, cy in [(200, self.height - 100), (500, self.height - 80),
                           (800, self.height - 110)]:
                for dx, dy, r in [(0, 0, 30), (25, 10, 25), (-25, 10, 25),
                                  (50, 0, 20), (-50, 0, 20)]:
                    Ellipse(pos=(cx + dx - r, cy + dy - r), size=(r * 2, r * 2))

            Color(0.30, 0.60, 0.20)
            Rectangle(pos=(0, 0), size=(self.width, self.ground_y))
            Color(0.25, 0.50, 0.15)
            Rectangle(pos=(0, self.ground_y - 5), size=(self.width, 5))

            for block in self.blocks:
                block.draw(self.canvas)

            for bird in self.birds:
                bird.draw(self.canvas)

            self._draw_slingshot()

            if self.dragging and self.drag_pos:
                self._draw_aiming_pig()
                self._draw_trajectory()
            elif self.game_status == "aiming" and self.pigs_remaining > 0:
                Color(0.3, 0.75, 0.3)
                Ellipse(pos=(self.slingshot_x - 15, self.slingshot_y + 10), size=(30, 30))

            for pig in self.flying_pigs:
                if not pig.stopped:
                    pig.draw(self.canvas)

    def _draw_slingshot(self):
        Color(0.40, 0.25, 0.10)
        Rectangle(pos=(self.slingshot_x - 5, self.ground_y), size=(10, 60))
        Rectangle(pos=(self.slingshot_x - 20, self.slingshot_y + 30), size=(8, 40))
        Rectangle(pos=(self.slingshot_x + 12, self.slingshot_y + 30), size=(8, 40))
        Color(0.20, 0.10, 0.05)
        Line(points=[self.slingshot_x - 16, self.slingshot_y + 60,
                     self.slingshot_x, self.slingshot_y + 30,
                     self.slingshot_x + 16, self.slingshot_y + 60], width=3)

    def _clamp_drag(self):
        dx = self.drag_pos[0] - self.slingshot_x
        dy = self.drag_pos[1] - self.slingshot_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > self.max_drag:
            dx = dx / dist * self.max_drag
            dy = dy / dist * self.max_drag
        return dx, dy

    def _draw_aiming_pig(self):
        dx, dy = self._clamp_drag()
        px, py = self.slingshot_x + dx, self.slingshot_y + dy
        Color(0.20, 0.10, 0.05)
        Line(points=[self.slingshot_x - 16, self.slingshot_y + 60,
                     px, py,
                     self.slingshot_x + 16, self.slingshot_y + 60], width=3)
        Color(0.3, 0.75, 0.3)
        Ellipse(pos=(px - 15, py - 15), size=(30, 30))
        Color(1, 1, 1)
        Ellipse(pos=(px - 10, py + 2), size=(7, 7))
        Ellipse(pos=(px + 3, py + 2), size=(7, 7))
        Color(0, 0, 0)
        Ellipse(pos=(px - 7, py + 4), size=(4, 4))
        Ellipse(pos=(px + 6, py + 4), size=(4, 4))

    def _draw_trajectory(self):
        dx, dy = self._clamp_drag()
        vx = -dx * self.power
        vy = -dy * self.power
        x, y = self.slingshot_x, self.slingshot_y
        Color(1, 1, 1, 0.6)
        for i in range(60):
            vy -= GRAVITY * FIXED_DT
            x += vx * FIXED_DT
            y += vy * FIXED_DT
            if i % 4 == 0:
                Ellipse(pos=(x - 3, y - 3), size=(6, 6))
            if y < self.ground_y:
                break