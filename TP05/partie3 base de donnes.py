# Partie 3 - Q2 : connexion unique a une base de donnees puis fermeture
import sqlite3
import threading


class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_name=":memory:"):
        with cls._lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst.conn = sqlite3.connect(db_name, check_same_thread=False)
                cls._instance = inst
                print("Connexion ouverte a", db_name)
            else:
                print("Connexion existante reutilisee")
        return cls._instance

    def execute(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur.fetchall()

    def close(self):
        self.conn.close()
        DatabaseConnection._instance = None
        print("Connexion fermee")


if __name__ == "__main__":
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    print("db1 is db2 :", db1 is db2)
    db1.execute("CREATE TABLE users(id INTEGER, name TEXT)")
    db1.execute("INSERT INTO users VALUES (?, ?)", (1, "Ali"))
    db2.execute("INSERT INTO users VALUES (?, ?)", (2, "Sara"))
    print("SELECT * FROM users ->", db1.execute("SELECT * FROM users"))
    db1.close()
