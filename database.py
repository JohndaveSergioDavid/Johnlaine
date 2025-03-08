import sqlite3

def db():
    try:
        db = sqlite3.connect('database.db', check_same_thread=False)
        db.row_factory = sqlite3.Row
        return db
    except Exception as e:
        return str(e)