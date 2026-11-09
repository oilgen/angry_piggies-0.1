"""Таблица лидеров по уровням (красивая версия)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle


class LeaderboardScreen(Screen):
    def __init__(self, db, app, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.app = app

    def on_enter(self):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = FloatLayout()

        # Фон (небо + трава)
        with root.canvas.before:
            Color(0.53, 0.81, 0.92)
            Rectangle(pos=(0, 0), size=(1000, 600))
            Color(0.30, 0.60, 0.20)
            Rectangle(pos=(0, 0), size=(1000, 70))

        # Заголовок
        root.add_widget(Label(
            text="Таблица лидеров", font_size=40, bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None), height=60,
            pos_hint={"center_x": 0.5, "top": 0.96},
        ))

        levels = self.db.get_all_levels()
        
        # Контейнер для трёх колонок
        columns = BoxLayout(
            orientation="horizontal",
            spacing=20,
            padding=20,
            size_hint=(None, None),
            size=(940, 420),
            pos_hint={"center_x": 0.5, "center_y": 0.45},
        )

        for lvl in levels:
            card = self._create_level_card(lvl)
            columns.add_widget(card)

        root.add_widget(columns)

        # Кнопка "Назад"
        back = Button(
            text="← Назад", size_hint=(None, None), size=(150, 50),
            pos_hint={"x": 0.02, "top": 0.98},
            background_color=(0.9, 0.5, 0.2, 1), background_normal="",
            font_size=20, bold=True,
        )
        back.bind(on_press=lambda *_: setattr(self.app.sm, "current", "menu"))
        root.add_widget(back)

        self.add_widget(root)

    def _create_level_card(self, lvl):
        """Создаёт карточку для одного уровня."""
        card = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10,
            size_hint=(1, 1),
        )
        
        # Фон карточки с закруглёнными углами
        with card.canvas.before:
            Color(1, 1, 1, 0.95)
            self._card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        card.bind(pos=self._update_card_rect, size=self._update_card_rect)
        # Привязываем к card, чтобы self._card_rect не затирался
        card._card_rect = self._card_rect

        # Заголовок карточки
        card.add_widget(Label(
            text=f"[b]Уровень {lvl['id']}[/b]\n{lvl['name']}",
            markup=True, font_size=20, color=(0.1, 0.3, 0.6, 1),
            size_hint=(1, None), height=70,
        ))

        # Шапка таблицы
        header = GridLayout(cols=3, size_hint=(1, None), height=30, spacing=5)
        header.add_widget(Label(text="[b]Игрок[/b]", markup=True, color=(0, 0, 0, 1), font_size=14))
        header.add_widget(Label(text="[b]Время[/b]", markup=True, color=(0, 0, 0, 1), font_size=14))
        header.add_widget(Label(text="[b]Звёзды[/b]", markup=True, color=(0, 0, 0, 1), font_size=14))
        card.add_widget(header)

        # Разделитель
        line = BoxLayout(size_hint=(1, None), height=2)
        with line.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(pos=line.pos, size=line.size)
        card.add_widget(line)

        # Строки
        rows = self.db.get_leaderboard(lvl["id"], limit=10)
        
        if not rows:
            card.add_widget(Label(
                text="Пока нет рекордов", font_size=16, color=(0.5, 0.5, 0.5, 1),
                size_hint=(1, 1),
            ))
        else:
            # Используем ScrollView для длинных списков, если нужно
            for i, r in enumerate(rows):
                row = GridLayout(cols=3, size_hint=(1, None), height=25, spacing=5)
                
                # Чередование цветов строк
                bg_color = (0.95, 0.95, 0.95, 1) if i % 2 == 0 else (1, 1, 1, 1)
                with row.canvas.before:
                    Color(*bg_color)
                    self._row_rect = Rectangle(pos=row.pos, size=row.size)
                row.bind(pos=self._update_row_rect, size=self._update_row_rect)
                row._row_rect = self._row_rect

                name_label = Label(
                    text=r["nickname"],
                    color=(0, 0, 0, 1), font_size=14,
                    size_hint_x=0.4,
                )
                time_label = Label(
                    text=f"{r['best_time']:.1f}s",
                    color=(0.2, 0.6, 0.2, 1), font_size=14, bold=True,
                    size_hint_x=0.3,
                )
                stars_label = Label(
                    text="★" * r["stars"] + "☆" * (3 - r["stars"]),
                    color=(1.0, 0.8, 0.0, 1), font_size=14,
                    size_hint_x=0.3,
                )
                row.add_widget(name_label)
                row.add_widget(time_label)
                row.add_widget(stars_label)
                card.add_widget(row)

        return card

    def _update_card_rect(self, instance, value):
        instance._card_rect.pos = instance.pos
        instance._card_rect.size = instance.size

    def _update_row_rect(self, instance, value):
        instance._row_rect.pos = instance.pos
        instance._row_rect.size = instance.size