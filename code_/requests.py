import sqlite3





class Requests:
    def __init__(self, db_file: str):
        self.db_file = db_file
        with sqlite3.connect(self.db_file) as connection:
            connection.execute("PRAGMA encoding = 'UTF-8'")
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                login TEXT NOT NULL,
                type TEXT
            );""")
            connection.commit()


    def add(self, text: str, type_: str, login: str):      
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO requests (text, type, login) VALUES (?, ?, ?)", (text, type_, login))
            connection.commit()
            

    def exists(self, text: str, type_: str) -> bool:
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM requests WHERE text = ? AND type = ?", (text, type_))
            return cursor.fetchone() is not None


    def delete(self, id: int):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM requests WHERE id = ?", (id,))
            connection.commit()


    def delete_by_login(self, login: str):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM requests WHERE login = ?", (login,))
            connection.commit()


    def get(self, limit: int, type_: str = None) -> tuple[list[tuple[str, str]], int]:
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            
            if type_ is None:
                cursor.execute("SELECT COUNT(*) FROM requests")
            else:
                cursor.execute("SELECT COUNT(*) FROM requests WHERE type = ?", (type_,))
            total_count = cursor.fetchone()[0]

            if type_ is None:
                cursor.execute("SELECT id, text, login FROM requests LIMIT ?", (limit,))
            else:
                cursor.execute("SELECT id, text, login FROM requests WHERE type = ? LIMIT ?", (type_, limit))
            
            requests = [(id, text, login) for (id, text, login) in cursor.fetchall()]

        return requests, total_count






