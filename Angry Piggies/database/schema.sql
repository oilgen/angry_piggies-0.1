-- Схема БД игры Angry Piggies

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    episode TEXT NOT NULL,
    description TEXT,
    num_pigs INTEGER DEFAULT 1,
    difficulty INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS level_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level_id INTEGER NOT NULL,
    entity_type TEXT NOT NULL,
    x REAL NOT NULL,
    y REAL NOT NULL,
    width REAL DEFAULT 0,
    height REAL DEFAULT 0,
    material TEXT,
    hp INTEGER DEFAULT 100,
    is_bird INTEGER DEFAULT 0,
    FOREIGN KEY (level_id) REFERENCES levels(id)
);

CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    level_id INTEGER NOT NULL,
    stars INTEGER DEFAULT 0,
    best_time REAL DEFAULT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (level_id) REFERENCES levels(id),
    UNIQUE(player_id, level_id)
);

CREATE TABLE IF NOT EXISTS settings (
    player_id INTEGER PRIMARY KEY,
    sound INTEGER DEFAULT 1,
    music INTEGER DEFAULT 1,
    language TEXT DEFAULT 'ru',
    FOREIGN KEY (player_id) REFERENCES players(id)
);

INSERT OR IGNORE INTO levels (id, name, episode, description, num_pigs, difficulty) VALUES
(1, 'Первый полёт', 'Лес', 'Простое гнездо на дереве', 1, 1),
(2, 'Двойная защита', 'Пляж', 'Два гнезда на песке', 2, 2),
(3, 'Горная крепость', 'Горы', 'Крепкая башня с тремя гнёздами', 3, 3);

-- УРОВЕНЬ 1: деревянная П-образная конструкция
INSERT OR IGNORE INTO level_entities (level_id, entity_type, x, y, width, height, material, hp, is_bird) VALUES
(1, 'block', 600, 70, 30, 180, 'wood', 100, 0),
(1, 'block', 850, 70, 30, 180, 'wood', 100, 0),
(1, 'block', 600, 250, 280, 30, 'wood', 100, 0),
(1, 'bird', 725, 280, 40, 40, NULL, 50, 1);

-- УРОВЕНЬ 2: дерево + камень, две птицы
INSERT OR IGNORE INTO level_entities (level_id, entity_type, x, y, width, height, material, hp, is_bird) VALUES
(2, 'block', 600, 70, 30, 150, 'wood', 100, 0),
(2, 'block', 720, 70, 30, 150, 'wood', 100, 0),
(2, 'block', 600, 220, 150, 30, 'wood', 100, 0),
(2, 'bird', 660, 250, 40, 40, NULL, 50, 1),
(2, 'block', 870, 70, 30, 150, 'stone', 200, 0),
(2, 'block', 990, 70, 30, 150, 'stone', 200, 0),
(2, 'block', 870, 220, 150, 30, 'stone', 200, 0),
(2, 'bird', 925, 250, 40, 40, NULL, 50, 1);

-- УРОВЕНЬ 3: каменное основание + дерево, три птицы СВЕРХУ
INSERT OR IGNORE INTO level_entities (level_id, entity_type, x, y, width, height, material, hp, is_bird) VALUES
-- Каменное основание
(3, 'block', 580, 70, 40, 100, 'stone', 200, 0),
(3, 'block', 680, 70, 40, 100, 'stone', 200, 0),
(3, 'block', 780, 70, 40, 100, 'stone', 200, 0),
(3, 'block', 880, 70, 40, 100, 'stone', 200, 0),
-- Деревянная платформа поверх камня
(3, 'block', 580, 170, 340, 40, 'wood', 100, 0),
-- Деревянные колонны для второго этажа
(3, 'block', 630, 210, 40, 100, 'wood', 100, 0),
(3, 'block', 830, 210, 40, 100, 'wood', 100, 0),
-- Верхняя деревянная перекладина
(3, 'block', 630, 310, 240, 40, 'wood', 100, 0),
-- ПТИЦЫ СВЕРХУ (на перекладине y=350, так как 310+40=350)
(3, 'bird', 640, 350, 40, 40, NULL, 50, 1),
(3, 'bird', 730, 350, 40, 40, NULL, 50, 1),
(3, 'bird', 820, 350, 40, 40, NULL, 50, 1);