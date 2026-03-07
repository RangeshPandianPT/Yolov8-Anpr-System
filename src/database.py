import sqlite3
import Levenshtein

class PlateVerifier:
    def __init__(self, db_path='data/plates.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """
        Initialize the SQLite database with an authorized_plates table.
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
        # Insert some dummy data for testing
        cursor.execute("INSERT OR IGNORE INTO authorized_plates (plate_number, owner_name) VALUES ('MH12AB1234', 'John Doe')")
        cursor.execute("INSERT OR IGNORE INTO authorized_plates (plate_number, owner_name) VALUES ('KA01XY5678', 'Jane Smith')")
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
                
        if min_distance <= threshold:
            return True, best_match, min_distance
        
        return False, best_match, min_distance

if __name__ == "__main__":
    pass
