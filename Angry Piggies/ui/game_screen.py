"""Игровой экран уровня."""

import time

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

from ui.game_widget import GameWidget


class GameScreen(Screen):
    def __init__(self, db, level_id, app, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.level_id = level_id
        self.app = app
        self.start_time = time.time()

        self.level_data = db.get_level(level_id)
        entities = db.get_level_entities(level_id)

        self.main_layout = FloatLayout()

        self.game_widget = GameWidget(
            level_data=self.level_data,
            entities_data=entities,
            on_win=self._on_win,
            on_lose=self._on_lose,
            size_hint=(1, 1), pos=(0, 0),
        )
        self.main_layout.add_widget(self.game_widget)

        top = BoxLayout(size_hint=(1, None), height=60,
                        pos_hint={"x": 0, "top": 1}, padding=10, spacing=10)
        with top.canvas.before:
            Color(0.15, 0.15, 0.2, 0.85)
            Rectangle(pos=top.pos, size=top.size)

        back = Button(text="← Меню", size_hint=(None, 1), width=130,
                      background_color=(0.9, 0.5, 0.2, 1), background_normal="")
        back.bind(on_press=self._go_back)
        top.add_widget(back)

        top.add_widget(Label(
            text=f"Уровень {level_id}: {self.level_data['name']}",
            bold=True, font_size=22, color=(1, 1, 1, 1),
        ))
        top.add_widget(Label(
            text=f"Свинов: {self.level_data['num_pigs']}",
            bold=True, font_size=20, size_hint=(None, 1), width=160,
            color=(1, 1, 1, 1),
        ))
        self.main_layout.add_widget(top)

        self.main_layout.add_widget(Label(
            text="Оттяните свина на рогатке влево и отпустите",
            font_size=16, color=(1, 1, 1, 0.85),
            size_hint=(None, None), size=(600, 30),
            pos_hint={"center_x": 0.5, "y": 0.01},
        ))

        self.overlay = None
        self.add_widget(self.main_layout)

    def _create_overlay(self):
        self.overlay = FloatLayout(size_hint=(1, 1))
        with self.overlay.canvas.before:
            Color(0, 0, 0, 0.7)
            self._overlay_rect = Rectangle(pos=(0, 0), size=(10000, 10000))
        self.overlay.bind(size=self._resize_overlay)

        self.overlay_label = Label(
            text="", font_size=44, bold=True,
            pos_hint={"center_x": 0.5, "center_y": 0.6},
        )
        self.overlay.add_widget(self.overlay_label)

        self.next_btn = Button(
            text="Продолжить", font_size=22,
            size_hint=(None, None), size=(240, 70),
            pos_hint={"center_x": 0.5, "center_y": 0.35},
            background_color=(0.3, 0.7, 0.3, 1), background_normal="",
        )
        self.next_btn.bind(on_press=self._on_continue)
        self.overlay.add_widget(self.next_btn)

    def _resize_overlay(self, *args):
        if self.overlay:
            self._overlay_rect.size = self.overlay.size

    def _show_overlay(self, text, color, btn_text):
        if self.overlay is None:
            self._create_overlay()
        self.overlay_label.text = text
        self.overlay_label.color = color
        self.next_btn.text = btn_text
        if self.overlay.parent is None:
            self.main_layout.add_widget(self.overlay)

    def _go_back(self, *args):
        self.app.sm.current = "levels"

    def _on_win(self, stars):
        elapsed = time.time() - self.start_time
        self.db.save_progress(self.app.player_id, self.level_id, stars, elapsed)
        self._show_overlay(
            f"ПОБЕДА!\n{'★' * stars}{'☆' * (3 - stars)}\n⏱ {elapsed:.1f}s",
            (1.0, 0.9, 0.2, 1),
            "Следующий уровень",
        )

    def _on_lose(self):
        self._show_overlay("ПОРАЖЕНИЕ", (1.0, 0.3, 0.3, 1), "Повторить")

    def _on_continue(self, *args):
        if self.game_widget.game_status == "won":
            next_level = self.level_id + 1
            if next_level <= 3:
                self.app.start_level(next_level)
            else:
                self.app.sm.current = "levels"
        else:
            self.app.start_level(self.level_id)