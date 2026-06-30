import sqlite3
import Levenshtein
from datetime import datetime

class PlateVerifier:
    def __init__(self, db_path='data/plates.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """
        Initialize the SQLite database with authorized_plates and access_logs tables.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_plates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT UNIQUE NOT NULL,
                owner_name TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                plate_number TEXT NOT NULL,
                is_authorized BOOLEAN NOT NULL,
                matched_plate TEXT,
                confidence_score REAL
            )
        ''')
        # Insert some dummy data for testing if empty
        cursor.execute("SELECT COUNT(*) FROM authorized_plates")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT OR IGNORE INTO authorized_plates (plate_number, owner_name) VALUES ('MH12AB1234', 'John Doe')")
            cursor.execute("INSERT OR IGNORE INTO authorized_plates (plate_number, owner_name) VALUES ('KA01XY5678', 'Jane Smith')")
        conn.commit()
        conn.close()

    def get_all_plates(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM authorized_plates")
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return records

    def add_plate(self, plate_number, owner_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO authorized_plates (plate_number, owner_name) VALUES (?, ?)", (plate_number.upper(), owner_name))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False
        conn.close()
        return success

    def delete_plate(self, plate_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM authorized_plates WHERE id = ?", (plate_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def get_access_logs(self, limit=50):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM access_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return records

    def log_access(self, plate_number, is_authorized, matched_plate=None, confidence_score=0.0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO access_logs (timestamp, plate_number, is_authorized, matched_plate, confidence_score) VALUES (?, ?, ?, ?, ?)",
            (datetime.utcnow().isoformat() + "Z", plate_number, is_authorized, matched_plate, confidence_score)
        )
        conn.commit()
        conn.close()

    def verify_plate(self, predicted_plate, threshold=2):
        """
        Check if the predicted plate is in the database.
        Uses Levenshtein distance for fuzzy matching to handle OCR errors.
        Returns (is_authorized, matched_plate, distance).
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT plate_number FROM authorized_plates")
        records = cursor.fetchall()
        conn.close()
        
        best_match = None
        min_distance = float('inf')
        
        for record in records:
            db_plate = record[0]
            # Calculate edit distance between predicted and database plate
            dist = Levenshtein.distance(predicted_plate.upper(), db_plate.upper())
            if dist < min_distance:
                min_distance = dist
                best_match = db_plate
                
        is_authorized = min_distance <= threshold
        
        # Log the access attempt
        confidence_score = 1.0 / (min_distance + 1.0) # Simple pseudo-confidence based on distance
        self.log_access(predicted_plate.upper(), is_authorized, best_match if is_authorized else None, confidence_score)
        
        return is_authorized, best_match, min_distance

if __name__ == "__main__":
    pass
