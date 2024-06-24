import requests
import sqlite3
import time

class CanvasRecorder:
    def __init__(self, initial_image_url, db_file):
        self.initial_image_url = initial_image_url
        self.db_file = db_file
        self.start_time = time.time()
        self.conn = sqlite3.connect(self.db_file)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    x INTEGER NOT NULL,
                    y INTEGER NOT NULL,
                    color TEXT NOT NULL
                )
            """)

    def load_initial_image(self):
        response = requests.get(self.initial_image_url)
        with open(self.db_file.replace('.db', '_initial.png'), 'wb') as f:
            f.write(response.content)

    def record_change(self, change):
        timestamp = int((time.time() - self.start_time) * 1000)
        with self.conn:
            self.conn.execute("""
                INSERT INTO changes (timestamp, x, y, color)
                VALUES (?, ?, ?, ?)
            """, (timestamp, change['x'], change['y'], change['color']))

    def close(self):
        self.conn.close()