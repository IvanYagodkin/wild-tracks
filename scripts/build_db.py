import os
import sqlite3
import csv

# Пути
D = "/data/data/com.termux/files/home/wild-tracks"
DB = f"{D}/data/wild_tracks.db"
SCHEMA = f"{D}/data/schema.sql"
SPECIES_CSV = f"{D}/data/species.csv"
TRACKS_CSV = f"{D}/data/tracks.csv"

# Удаляем старую базу, если есть
if os.path.exists(DB):
    os.remove(DB)
    print("✅ Удалена старая база")

# Создаём новую и применяем схему
conn = sqlite3.connect(DB)
conn.executescript(open(SCHEMA, 'r', encoding='utf-8').read())
print("✅ Применена схема")

# Загружаем виды
cur = conn.cursor()
for row in csv.DictReader(open(SPECIES_CSV, encoding='utf-8')):
    cur.execute("""
        INSERT INTO species (latin_name, common_name_ru, common_name_en,
        typical_habitat, avg_track_length, avg_track_width)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row['latin_name'],
        row['common_name_ru'],
        row['common_name_en'],
        row['typical_habitat'],
        float(row['avg_track_length']) if row['avg_track_length'] else None,
        float(row['avg_track_width']) if row['avg_track_width'] else None
    ))
print("✅ Загружены виды")

# Загружаем следы
for row in csv.DictReader(open(TRACKS_CSV, encoding='utf-8')):
    cur.execute("""
        INSERT INTO tracks (species_id, image_path, length_cm, width_cm,
        region, habitat, date_seen, gps_lat, gps_lon, confidence, observer)
        VALUES ((SELECT id FROM species WHERE latin_name = ?), ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?)
    """, (
        row['latin_name'],
        row['image_path'],
        float(row['length_cm']),
        float(row['width_cm']),
        row['region'],
        row['habitat'],
        row['date_seen'],
        float(row['gps_lat']) if row['gps_lat'] else None,
        float(row['gps_lon']) if row['gps_lon'] else None,
        float(row['confidence']),
        row['observer']
    ))
print("✅ Загружены следы")

# Сохраняем и закрываем
conn.commit()
conn.close()
print("🎉 Готово: wild_tracks.db создана!")
