"""Экран регистрации / входа."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, Ellipse


class AuthScreen(Screen):
    def __init__(self, db, app, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.app = app
        self._build()

    def _build(self):
        self.clear_widgets()
        root = FloatLayout()

        with root.canvas.before:
            Color(0.53, 0.81, 0.92)
            Rectangle(pos=(0, 0), size=(1000, 600))
            Color(0.30, 0.60, 0.20)
            Rectangle(pos=(0, 0), size=(1000, 100))
            Color(1.0, 0.9, 0.3)
            Ellipse(pos=(860, 480), size=(80, 80))

        title = Label(
            text="ANGRY PIGGIES",
            font_size=54,
            bold=True,
            color=(1.0, 0.85, 0.1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.85},
        )
        root.add_widget(title)

        box = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(420, 260),
            pos_hint={"center_x": 0.5, "center_y": 0.45},
            spacing=12,
            padding=20,
        )

        self.nick_input = TextInput(
            hint_text="Никнейм",
            multiline=False,
            font_size=20,
            size_hint=(1, None),
            height=50,
        )
        self.pass_input = TextInput(
            hint_text="Пароль",
            password=True,
            multiline=False,
            font_size=20,
            size_hint=(1, None),
            height=50,
        )
        box.add_widget(self.nick_input)
        box.add_widget(self.pass_input)

        buttons = BoxLayout(spacing=10, size_hint=(1, None), height=60)
        login_btn = Button(
            text="Войти",
            font_size=20,
            background_color=(0.3, 0.7, 0.3, 1),
            background_normal="",
        )
        login_btn.bind(on_press=self._on_login)
        reg_btn = Button(
            text="Регистрация",
            font_size=20,
            background_color=(0.9, 0.5, 0.2, 1),
            background_normal="",
        )
        reg_btn.bind(on_press=self._on_register)
        buttons.add_widget(login_btn)
        buttons.add_widget(reg_btn)
        box.add_widget(buttons)

        self.error_label = Label(
            text="",
            font_size=16,
            color=(1, 0.3, 0.3, 1),
            size_hint=(1, None),
            height=30,
        )
        box.add_widget(self.error_label)

        root.add_widget(box)
        self.add_widget(root)

    def _on_register(self, *args):
        nickname = self.nick_input.text.strip()
        password = self.pass_input.text
        if not nickname or not password:
            self.error_label.text = "Введите никнейм и пароль"
            return
        pid = self.db.register_player(nickname, password)
        if pid is None:
            self.error_label.text = "Никнейм уже занят"
            return
        self.app.set_player(pid)
        self.app.sm.current = "menu"

    def _on_login(self, *args):
        nickname = self.nick_input.text.strip()
        password = self.pass_input.text
        if not nickname or not password:
            self.error_label.text = "Введите никнейм и пароль"
            return
        pid = self.db.login_player(nickname, password)
        if pid is None:
            self.error_label.text = "Неверный никнейм или пароль"
            return
        self.app.set_player(pid)
        self.app.sm.current = "menu"