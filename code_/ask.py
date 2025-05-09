import sqlite3
from fuzzywuzzy import process
from types import SimpleNamespace as nspace




class Ask:
    def __init__(self, db_file: str):
        self.db_file = db_file
        with sqlite3.connect(self.db_file) as connection:
            connection.execute("PRAGMA encoding = 'UTF-8'")
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                question TEXT NOT NULL PRIMARY KEY,
                answer TEXT, 
                answered INTEGER NOT NULL, 
                asked_login TEXT
            );""")
            connection.commit()

    def add_question(self, question_str: str, login: str):      
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO questions (question, answered, asked_login) VALUES (?, ?, ?)", (question_str, False, login))
            connection.commit()
        return question_str
            
    def question_exists(self, question_str: str) -> bool:
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM questions WHERE question = ?", (question_str,))
            return cursor.fetchone() is not None

    def delete(self, question_str: str) -> bool:
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            
            cursor.execute("SELECT 1 FROM questions WHERE question = ? AND answered = 0", (question_str,))
            if cursor.fetchone() is None:
                return False
            
            cursor.execute("DELETE FROM questions WHERE question = ?", (question_str,))
            connection.commit()
            return True

    def delete_by_login(self, login: str):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM questions WHERE asked_login = ? AND answered = 0", (login,))
            connection.commit()

    def answer(self, question_str: str, answer_str: str) -> bool:
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT 1 FROM questions WHERE question = ? AND answered = 0", (question_str,))
            if cursor.fetchone() is None:
                return False
            
            cursor.execute("UPDATE questions SET answer = ?, answered = ? WHERE question = ?", (answer_str, True, question_str))
            connection.commit()
            return True

    def get_similar_answer(self, request: str) -> list[str]:
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT question, answer FROM questions WHERE answered = ?", (True,))

            questions = {question_str: answer_str for question_str, answer_str in cursor.fetchall()}

            extract = process.extract(request, questions.keys(), limit=5)

            return [(question_str, questions[question_str]) for question_str, score in extract if score > 50]

    def get_answer(self, request: str) -> str:
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT answer FROM questions WHERE question = ? AND answered = ?", (request, True))
            answer = cursor.fetchone()

            if answer is None:
                return None
            
            return answer[0]
            
    def get_unanswered(self, limit: int) -> list[str]:
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT question, asked_login FROM questions WHERE answered = 0 ORDER BY question DESC LIMIT ?", (limit, ))
            questions = [(question_str, login) for question_str, login, *_ in cursor.fetchall()]
            cursor.execute("SELECT COUNT(*) FROM questions WHERE answered = 0")
            count, = cursor.fetchone()
            return questions, count

    def display_all_questions(self):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT question, answer, answered FROM questions")
            rows = cursor.fetchall()

        for question_str, answer_str, answered in rows: 
            print(f"Вопрос: {question_str}, Ответ: {answer_str}, Ответили: {bool(answered)}")

    @staticmethod
    def generate(initial_file):
        ask = Ask("assets/ask.db")
        with open(initial_file, "r", encoding="utf-8") as file:
            for line in file.readlines():
                question_str, answer_str = line.split("=")
                if answer_str[-1] == '\n':
                    answer_str = answer_str[:-1]

                print("Добавляем", repr(question_str), repr(answer_str))

                ask.add_question(question_str, None)
                ask.answer(question_str, answer_str)
            



            


   
    

if __name__ == "__main__":
    Ask.generate("assets/examples/ask.txt")
    # ask = Ask("assets/ask.db")
    # ask.display_all_questions()
    

