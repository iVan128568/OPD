import sqlite3
import json
import bcrypt
from types import SimpleNamespace as nspace

class Users:
    def __init__(self, db_name: str = 'users.db') -> None:
        self.db_name = db_name
        self.create_tables()

    def create_tables(self) -> None:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                login TEXT PRIMARY KEY,
                password_hash BLOB NOT NULL,
                is_admin INTEGER NOT NULL,
                chat_ids TEXT NOT NULL,
                contract_number TEXT,
                dorm TEXT,
                room_number INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arc_users (
                chat_id TEXT PRIMARY KEY,
                login TEXT NOT NULL
            )
        ''')

        connection.commit()
        connection.close()

    def get_all(self, limit: int) -> list[dict]:
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            
            cursor.execute("SELECT * FROM users LIMIT ?", (limit,))
            rows = cursor.fetchall()
            users = [nspace(login = row[0], password_hash = row[1], is_admin = bool(row[2]), chat_ids = json.loads(row[3])) for row in rows]

            cursor.execute("SELECT COUNT(*) FROM users")
            count, = cursor.fetchone()

            return users, count

    def add_user(self, login: str, password: str, is_admin: bool, contract_number: str = None, dorm: str = None, room_number: int = None) -> None:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO users (login, password_hash, is_admin, chat_ids, contract_number, dorm, room_number) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (login, bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()), int(is_admin), json.dumps([]), contract_number, dorm, room_number))

        connection.commit()
        connection.close()

    def delete_user(self, login: str) -> None:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute('DELETE FROM users WHERE login = ?', (login,))
        
        cursor.execute('DELETE FROM arc_users WHERE login = ?', (login,))

        connection.commit()
        connection.close()

    def add_chat_id(self, login: str, chat_id: str) -> None:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute('SELECT chat_ids FROM users WHERE login = ?', (login,))
        result = cursor.fetchone()

        if result:
            current_ids = json.loads(result[0])
            if chat_id not in current_ids:
                current_ids.append(chat_id)
                cursor.execute('''
                    UPDATE users SET chat_ids = ? WHERE login = ?
                ''', (json.dumps(current_ids), login))
                cursor.execute('''
                    INSERT INTO arc_users (login, chat_id) VALUES (?, ?)
                ''', (login, chat_id))

        connection.commit()
        connection.close()

    def remove_chat_id(self, login: str, chat_id: str) -> None:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute('SELECT chat_ids FROM users WHERE login = ?', (login,))
        result = cursor.fetchone()

        if result:
            current_ids = json.loads(result[0])
            updated_ids = [cid for cid in current_ids if cid != chat_id]
            cursor.execute('''
                UPDATE users SET chat_ids = ? WHERE login = ?
            ''', (json.dumps(updated_ids), login))
            cursor.execute('''
                DELETE FROM arc_users WHERE chat_id = ?
            ''', (chat_id,))

        connection.commit()
        connection.close()

    def get_user_by_id(self, chat_id: str):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute('SELECT login FROM arc_users WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()

        connection.close()

        if result is None:
            return None

        return self.get_user_by_login(result[0]) 

    def get_user_by_login(self, login: str):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM users WHERE login = ?', (login,))
        result = cursor.fetchone()

        connection.close()

        if result is None:
            return None
        
        return nspace(login = result[0], password_hash = result[1], is_admin = bool(result[2]), chat_ids = json.loads(result[3]), contract_number = result[4], dorm = result[5], room_number = result[6])
    
    def check_password(self, password: str, password_hash: bytes):
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)
    
    @staticmethod
    def generate(initial_user_login, initial_user_password, db_name: str = "users.db"):
        users = Users(db_name)
        users.add_user(initial_user_login, initial_user_password, True)
        print("Generated user and exited")
        exit(0)

            


if __name__ == "__main__":
    Users.generate("amogus", "asdfg123", "assets/users.db")