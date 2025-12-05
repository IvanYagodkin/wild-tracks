#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

# Пути
DB_PATH = "/data/data/com.termux/files/home/wild-tracks/data/wild_tracks.db"
REMOTE_NAME = "yadisk"
REMOTE_PATH = f"{REMOTE_NAME}:/wild-tracks-backup"
CONFIG_FILE = "/data/data/com.termux/files/home/.config/rclone/rclone.conf"
BACKUP_NAME = f"wild_tracks_{datetime.now().strftime('%Y%m%d_%H%M')}.db"

def check_rclone_setup():
    """Проверяет, есть ли настройка yadisk"""
    try:
        result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
        return f"{REMOTE_NAME}:" in result.stdout
    except:
        return False

def check_db_exists():
    return os.path.exists(DB_PATH)

def run_backup():
    if not check_db_exists():
        print("❌ Ошибка: wild_tracks.db не найден. Запустите build_db.py сначала.")
        return

    if not check_rclone_setup():
        print("❌ Яндекс.Диск не настроен. Запустите:")
        print("   rclone config")
        print("   И создайте yadisk (выберите 60 → auto config)")
        return

    try:
        subprocess.run(["rclone", "copyto", DB_PATH, f"{REMOTE_PATH}/{BACKUP_NAME}"], check=True)
        print(f"✅ Успешно сохранено в облако: {BACKUP_NAME}")
    except subprocess.CalledProcessError:
        print("❌ Ошибка при загрузке в Яндекс.Диск")

if __name__ == "__main__":
    run_backup()
