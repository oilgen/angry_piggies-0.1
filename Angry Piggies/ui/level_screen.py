"""Экран выбора уровня с прогрессией."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle


class LevelSelectScreen(Screen):
    def __init__(self, db, app, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.app = app

    def on_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        layout = FloatLayout()

        with layout.canvas.before:
            Color(0.53, 0.81, 0.92)
            Rectangle(pos=(0, 0), size=(1000, 600))
            Color(0.30, 0.60, 0.20)
            Rectangle(pos=(0, 0), size=(1000, 80))

        layout.add_widget(Label(
            text="Выбор уровня", font_size=40, bold=True,
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.9},
        ))

        levels = self.db.get_all_levels()
        progress = self.db.get_player_progress(self.app.player_id) if self.app.player_id else {}

        for i, lvl in enumerate(levels):
            x = 0.22 + i * 0.28
            unlocked = self.app.player_id and self.db.is_level_unlocked(self.app.player_id, lvl["id"])
            stars = progress.get(lvl["id"], {}).get("stars", 0)
            stars_str = "★" * stars + "☆" * (3 - stars)
            best = progress.get(lvl["id"], {}).get("best_time")
            best_str = f"\n⏱ {best:.1f}s" if best else ""

            text = f"[b]{lvl['name']}[/b]\n{lvl['episode']}\n{stars_str}{best_str}"
            if not unlocked:
                text += "\n🔒 закрыт"

            btn = Button(
                text=text, markup=True, font_size=18,
                size_hint=(None, None), size=(220, 220),
                pos_hint={"center_x": x, "center_y": 0.5},
                background_color=(0.9, 0.7, 0.3, 1) if unlocked else (0.5, 0.5, 0.5, 1),
                background_normal="",
                disabled=not unlocked,
            )
            btn.level_id = lvl["id"]
            btn.bind(on_press=self._on_level_pick)
            layout.add_widget(btn)

        back = Button(
            text="← Назад", size_hint=(None, None), size=(150, 50),
            pos_hint={"x": 0.02, "top": 0.98},
            background_color=(0.9, 0.5, 0.2, 1), background_normal="",
        )
        back.bind(on_press=lambda *_: setattr(self.app.sm, "current", "menu"))
        layout.add_widget(back)

        self.add_widget(layout)

    def _on_level_pick(self, btn):
        self.app.start_level(btn.level_id)