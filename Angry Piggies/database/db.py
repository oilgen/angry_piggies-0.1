"""Обёртка над SQLite для игры Angry Piggies."""

import sqlite3
import hashlib
from pathlib import Path


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def init_schema(self):
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()
        sql = sql.lstrip("\ufeff")
        lines = [ln for ln in sql.splitlines() if not ln.strip().startswith("```")]
        sql = "\n".join(lines)
        self.cursor.executescript(sql)
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()

    # ---------- Игроки ----------

    def register_player(self, nickname, password):
        """Регистрирует нового игрока. Возвращает id или None, если ник занят."""
        try:
            self.cursor.execute(
                "INSERT INTO players (nickname, password_hash) VALUES (?, ?)",
                (nickname, _hash(password)),
            )
            self.conn.commit()
            pid = self.cursor.lastrowid
            self.cursor.execute(
                "INSERT INTO settings (player_id) VALUES (?)", (pid,)
            )
            self.conn.commit()
            return pid
        except sqlite3.IntegrityError:
            return None

    def login_player(self, nickname, password):
        """Проверяет логин/пароль. Возвращает id или None."""
        self.cursor.execute(
            "SELECT id, password_hash FROM players WHERE nickname = ?",
            (nickname,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        if row["password_hash"] != _hash(password):
            return None
        return row["id"]

    def get_player(self, player_id):
        self.cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
        return self.cursor.fetchone()

    def get_total_stars(self, player_id):
        self.cursor.execute(
            "SELECT COALESCE(SUM(stars), 0) AS total FROM progress WHERE player_id = ?",
            (player_id,),
        )
        return self.cursor.fetchone()["total"]

    # ---------- Уровни ----------

    def get_all_levels(self):
        self.cursor.execute("SELECT * FROM levels ORDER BY id")
        return self.cursor.fetchall()

    def get_level(self, level_id):
        self.cursor.execute("SELECT * FROM levels WHERE id = ?", (level_id,))
        return self.cursor.fetchone()

    def get_level_entities(self, level_id):
        self.cursor.execute(
            "SELECT * FROM level_entities WHERE level_id = ? ORDER BY id",
            (level_id,),
        )
        return self.cursor.fetchall()

    # ---------- Прогресс ----------

    def get_player_progress(self, player_id):
        self.cursor.execute(
            "SELECT * FROM progress WHERE player_id = ?", (player_id,)
        )
        return {row["level_id"]: dict(row) for row in self.cursor.fetchall()}

    def is_level_unlocked(self, player_id, level_id):
        """Уровень 1 всегда открыт; N открывается, если пройден N-1."""
        if level_id == 1:
            return True
        self.cursor.execute(
            "SELECT 1 FROM progress WHERE player_id = ? AND level_id = ? AND stars > 0",
            (player_id, level_id - 1),
        )
        return self.cursor.fetchone() is not None

    def save_progress(self, player_id, level_id, stars, time_seconds):
        """Сохраняет прогресс и лучшее время."""
        self.cursor.execute(
            "SELECT * FROM progress WHERE player_id = ? AND level_id = ?",
            (player_id, level_id),
        )
        existing = self.cursor.fetchone()
        if existing:
            best_time = existing["best_time"]
            if best_time is None or time_seconds < best_time:
                best_time = time_seconds
            if stars > existing["stars"]:
                self.cursor.execute(
                    "UPDATE progress SET stars = ?, best_time = ?, completed_at = CURRENT_TIMESTAMP "
                    "WHERE player_id = ? AND level_id = ?",
                    (stars, best_time, player_id, level_id),
                )
            else:
                self.cursor.execute(
                    "UPDATE progress SET best_time = ? WHERE player_id = ? AND level_id = ?",
                    (best_time, player_id, level_id),
                )
        else:
            self.cursor.execute(
                "INSERT INTO progress (player_id, level_id, stars, best_time, completed_at) "
                "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (player_id, level_id, stars, time_seconds),
            )
        self.conn.commit()

    # ---------- Таблица лидеров ----------

    def get_leaderboard(self, level_id, limit=10):
        """Возвращает лучшие результаты по времени для уровня."""
        self.cursor.execute(
            """SELECT p.nickname, pr.stars, pr.best_time
               FROM progress pr
               JOIN players p ON p.id = pr.player_id
               WHERE pr.level_id = ? AND pr.best_time IS NOT NULL
               ORDER BY pr.best_time ASC
               LIMIT ?""",
            (level_id, limit),
        )
        return self.cursor.fetchall()