import sqlite3
import datetime
import time



class Plan:

    def __init__(self, db_name='plan.db'):
        self.db_name = db_name
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plan (
                    room_number INTEGER NOT NULL PRIMARY KEY,
                    date INTEGER NOT NULL
                )
            ''')
            connection.commit()


    def get(self):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT room_number, date FROM plan ORDER BY date")
            
            return [(self.posix_to_date(date), room_number) for room_number, date in cursor.fetchall()]


    def set(self, plan_str: str):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()

            cursor.execute("DELETE FROM plan")

            if plan := self.parse_plan_str(plan_str):
                for room, date in plan:
                    cursor.execute('''
                        INSERT OR REPLACE INTO plan (room_number, date) VALUES (?, ?)
                    ''', (room, date))

            connection.commit()

            return bool(plan)
        

    def unset(self):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM plan")
            connection.commit()


    def parse_plan_str(self, plan_str: str):
        result = []
        plan_str = plan_str.replace("-", "")
        for line in plan_str.split("\n"):
            if line.strip() == "":
                continue

            try:
                date_str, room_str = [str_.strip() for str_ in line.split(" ", 1)]
                date = self.date_to_posix(date_str)
                room = int(room_str)
            except ValueError:
                return None
            
            result.append((room, date))
        return result
    

    @staticmethod
    def date_to_posix(date_str):
        current_year = datetime.datetime.now().year
        date_obj = datetime.datetime.strptime(date_str, "%d.%m").replace(year=current_year)
        posix_timestamp = int(time.mktime(date_obj.timetuple()))
        return posix_timestamp
    

    @staticmethod
    def posix_to_date(posix_timestamp):
        date_obj = datetime.datetime.fromtimestamp(posix_timestamp)
        date_str = date_obj.strftime("%d.%m")
        return date_str



