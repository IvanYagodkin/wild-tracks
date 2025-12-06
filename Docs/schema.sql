-- -----------------------------------------
-- Схема базы данных: wild-tracks
-- Проект: Идентификация следов диких животных
-- -----------------------------------------

-- Удаляем таблицы, если уже существуют (для пересоздания)
DROP TABLE IF EXISTS tracks;
DROP TABLE IF EXISTS species;

-- Включаем внешние ключи (важно для SQLite)
PRAGMA foreign_keys = ON;

-- -----------------------------------------
-- Таблица: species
-- Хранит информацию о видах животных
-- -----------------------------------------
CREATE TABLE species (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latin_name TEXT NOT NULL UNIQUE,           -- Латинское название (Ursus arctos)
    common_name_ru TEXT NOT NULL,              -- Русское название (Бурый медведь)
    common_name_en TEXT,                       -- Английское название (Brown Bear)
    typical_habitat TEXT,                      -- Типичная среда обитания (тайга, болото)
    avg_track_length REAL,                     -- Средняя длина следа (см)
    avg_track_width REAL,                      -- Средняя ширина следа (см)
    description TEXT                           -- Дополнительное описание (по желанию)
);

-- Индекс по латинскому названию — ускоряет поиск
CREATE INDEX IF NOT EXISTS idx_species_name ON species(latin_name);

-- -----------------------------------------
-- Таблица: tracks
-- Хранит данные о найденных следах
-- -----------------------------------------
CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id INTEGER NOT NULL,               -- Ссылка на species(id)
    image_path TEXT NOT NULL,                  -- Путь к фото следа
    length_cm REAL,                            -- Длина следа (см)
    width_cm REAL,                             -- Ширина следа (см)
    region TEXT,                               -- Регион наблюдения (Карелия, Алтай)
    habitat TEXT,                              -- Конкретный тип местности (сосновый бор)
    date_seen TEXT,                            -- Дата наблюдения (ГГГГ-М-ДД или ГГГГ-ММ-ДД)
    gps_lat REAL,                              -- Широта (от -90 до 90)
    gps_lon REAL,                              -- Долгота (от -180 до 180)
    confidence REAL DEFAULT 1.0,               -- Уверенность в определении (0.0–1.0)
    observer TEXT DEFAULT 'field_researcher',  -- Кто обнаружил
    notes TEXT,                                -- Примечания
    created_at TEXT DEFAULT (datetime('now', 'localtime')), -- Время добавления в базу

    -- Ограничения (CHECK)
    CHECK (length_cm > 0 AND length_cm < 100),
    CHECK (width_cm > 0 AND width_cm < 100),
    CHECK (gps_lat >= -90.0 AND gps_lat <= 90.0),
    CHECK (gps_lon >= -180.0 AND gps_lon <= 180.0),
    CHECK (confidence >= 0.0 AND confidence <= 1.0),
    -- CHECK (date_seen GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]?-[0-9][0-9]?')  -- временно отключено,

    -- Связь с таблицей species
    FOREIGN KEY (species_id) REFERENCES species (id) ON DELETE CASCADE
);

-- -----------------------------------------
-- Индексы для ускорения запросов
-- -----------------------------------------
CREATE INDEX IF NOT EXISTS idx_tracks_species ON tracks(species_id);
CREATE INDEX IF NOT EXISTS idx_tracks_region ON tracks(region);
CREATE INDEX IF NOT EXISTS idx_tracks_date ON tracks(date_seen);
CREATE INDEX IF NOT EXISTS idx_tracks_observer ON tracks(observer);
CREATE INDEX IF NOT EXISTS idx_tracks_created ON tracks(created_at);
