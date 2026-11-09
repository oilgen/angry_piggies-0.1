"""Главное меню."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse


class MenuScreen(Screen):
    def __init__(self, db, app, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.app = app
        self._build()

    def _build(self):
        self.clear_widgets()
        layout = FloatLayout()

        with layout.canvas.before:
            Color(0.53, 0.81, 0.92)
            Rectangle(pos=(0, 0), size=(1000, 600))
            Color(0.30, 0.60, 0.20)
            Rectangle(pos=(0, 0), size=(1000, 100))
            Color(1.0, 0.9, 0.3)
            Ellipse(pos=(860, 480), size=(80, 80))

        layout.add_widget(Label(
            text="ANGRY PIGGIES",
            font_size=72, bold=True,
            color=(1.0, 0.85, 0.1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.78},
        ))
        layout.add_widget(Label(
            text="Свиньи против птиц",
            font_size=28, color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.68},
        ))

        pid = self.app.player_id
        if pid:
            player = self.db.get_player(pid)
            stars = self.db.get_total_stars(pid)
            layout.add_widget(Label(
                text=f"Игрок: {player['nickname']}    Звёзд: {stars}",
                font_size=20, color=(1, 1, 1, 1),
                pos_hint={"x": 0.02, "top": 0.98},
            ))

        btns = [
            ("ИГРАТЬ", self._on_play),
            ("Таблица лидеров", self._on_leaderboard),
            ("Выйти из аккаунта", self._on_logout),
            ("Выход", self._on_quit),
        ]
        y = 0.45
        for text, cb in btns:
            b = Button(
                text=text, font_size=26, bold=True,
                size_hint=(None, None), size=(340, 60),
                pos_hint={"center_x": 0.5, "center_y": y},
                background_color=(0.9, 0.5, 0.2, 1),
                background_normal="",
            )
            b.bind(on_press=cb)
            layout.add_widget(b)
            y -= 0.12

        self.add_widget(layout)

    def _on_play(self, *args):
        self.app.sm.current = "levels"

    def _on_leaderboard(self, *args):
        self.app.sm.current = "leaderboard"

    def _on_logout(self, *args):
        self.app.player_id = None
        self.app.sm.current = "auth"

    def _on_quit(self, *args):
        self.app.stop()