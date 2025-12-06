from flask import Flask, request, render_template_string, send_from_directory
import sqlite3
import csv
import os
import time
import subprocess

app = Flask(__name__)

# Пути
DATA_DIR = "data"
PHOTOS_DIR = os.path.join(DATA_DIR, "photos")
DB_PATH = os.path.join(DATA_DIR, "wild_tracks.db")
CSV_PATH = os.path.join(DATA_DIR, "tracks.csv")

# Создаём папки
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)

# Инициализация базы
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY,
            length REAL,
            width REAL,
            species TEXT,
            photo TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Обновление CSV
def update_csv():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracks")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        writer.writerows(rows)
    conn.close()

init_db()
update_csv()

# Главная страница
@app.route("/")
def index():
    return render_template_string('''
    <h2>Добавить след</h2>
    <form method="post" action="/add">
        Длина (см): <input type="number" step="0.1" name="length" required><br><br>
        Ширина (см): <input type="number" step="0.1" name="width" required><br><br>
        Вид: 
        <select name="species" required>
            <option value="Лось">Лось</option>
            <option value="Кабан">Кабан</option>
            <option value="Лиса">Лиса</option>
            <option value="Заяц">Заяц</option>
            <option value="Волк">Волк</option>
            <option value="Рысь">Рысь</option>
            <option value="Медведь">Медведь</option>
            <option value="Другое">Другое</option>
        </select><br><br>
        <button type="button" onclick="capturePhoto()">📸 Сфотографировать</button>
        <input type="hidden" name="photo" id="photo" value="">
        <div id="photo-preview" style="margin-top: 10px;"></div><br>
        <button type="submit">Добавить</button>
    </form>
    <p><a href="/all">Все следы</a> | <a href="/download">Скачать CSV</a></p>

    <script>
        function capturePhoto() {
            fetch('/capture-photo')
                .then(response => response.json())
                .then(data => {
                    if (data.photo) {
                        document.getElementById('photo').value = data.photo;
                        document.getElementById('photo-preview').innerHTML = 
                            '<img src="/photos/' + data.photo + '" width="150" style="border: 1px solid #ccc">';
                    } else {
                        alert('❌ Ошибка: ' + (data.error || 'Не удалось сделать фото'));
                    }
                })
                .catch(() => alert('❌ Ошибка: сервер не отвечает'));
        }
    </script>
    ''')

# Сделать фото — с защитой
@app.route("/capture-photo")
def capture_photo():
    photo_filename = f"photo_{int(time.time())}.jpg"
    photo_path = os.path.join(PHOTOS_DIR, photo_filename)
    try:
        result = subprocess.run(
            ["termux-camera-photo", "-c", "0", photo_path],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0 and os.path.exists(photo_path):
            return {"photo": photo_filename}
        else:
            return {"error": f"Ошибка: {result.stderr or 'Фото не сохранено'}"}
    except Exception as e:
        return {"error": f"Ошибка: {str(e)}"}

# Отдаём фото
@app.route("/photos/<filename>")
def get_photo(filename):
    return send_from_directory(PHOTOS_DIR, filename)

# Добавление следа
@app.route("/add", methods=["POST"])
def add_track():
    try:
        length = float(request.form["length"])
        width = float(request.form["width"])
        species = request.form["species"]
        photo = request.form.get("photo", "")
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO tracks (length, width, species, photo) VALUES (?, ?, ?, ?)",
                     (length, width, species, photo))
        conn.commit()
        update_csv()
        conn.close()
        return f'''
        <h3>✅ След добавлен!</h3>
        {f'<p><img src="/photos/{photo}" width="200"></p>' if photo else ''}
        <p><a href="/">Добавить ещё</a> | <a href="/all">Посмотреть все</a></p>
        '''
    except Exception as e:
        return f"<h3>❌ Ошибка: {str(e)}</h3><p><a href='/'>Назад</a></p>"

# Все следы
@app.route("/all")
def all_tracks():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        table = "<h2>Все следы</h2><table border='1' cellpadding='5'>"
        table += "<tr><th>ID</th><th>Длина</th><th>Ширина</th><th>Вид</th><th>Фото</th><th>Дата</th></tr>"
        for row in rows:
            photo_cell = f'<img src="/photos/{row["photo"]}" width="60">' if row["photo"] else "—"
            table += f"<tr><td>{row['id']}</td><td>{row['length']}</td><td>{row['width']}</td><td>{row['species']}</td><td>{photo_cell}</td><td>{row['timestamp']}</td></tr>"
        table += "</table><p><a href='/'>На главную</a></p>"
        return table
    except Exception as e:
        return f"<h3>❌ Ошибка: {str(e)}</h3><p><a href='/'>Назад</a></p>"

# Скачать CSV
@app.route("/download")
def download_csv():
    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        return content, 200, {
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment; filename=tracks.csv"
        }
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
