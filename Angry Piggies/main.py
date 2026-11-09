"""Angry Piggies — точка входа."""

from kivy.config import Config
Config.set("graphics", "fps", "60")
Config.set("graphics", "vsync", "1")

import sys
from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from database.db import Database
from ui.auth_screen import AuthScreen
from ui.menu_screen import MenuScreen
from ui.level_screen import LevelSelectScreen
from ui.leaderboard_screen import LeaderboardScreen
from ui.game_screen import GameScreen


class AngryPiggiesApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db_path = Path(__file__).parent / "angry_piggies.db"
        self.db = Database(str(db_path))
        self.db.connect()
        self.db.init_schema()
        self.player_id = None
        self.sm = None

    def build(self):
        Window.size = (1000, 600)
        Window.clearcolor = (0.53, 0.81, 0.92, 1)

        self.sm = ScreenManager(transition=FadeTransition(duration=0.3))

        self.sm.add_widget(AuthScreen(name="auth", db=self.db, app=self))
        self.sm.add_widget(MenuScreen(name="menu", db=self.db, app=self))
        self.sm.add_widget(LevelSelectScreen(name="levels", db=self.db, app=self))
        self.sm.add_widget(LeaderboardScreen(name="leaderboard", db=self.db, app=self))

        self.sm.current = "auth"
        return self.sm

    def set_player(self, player_id):
        self.player_id = player_id

    def start_level(self, level_id):
        for screen in list(self.sm.screens):
            if screen.name == "game":
                self.sm.remove_widget(screen)
        game = GameScreen(name="game", db=self.db, level_id=level_id, app=self)
        self.sm.add_widget(game)
        self.sm.current = "game"

    def on_stop(self):
        self.db.close()


if __name__ == "__main__":
    AngryPiggiesApp().run()