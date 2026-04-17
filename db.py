import sqlite3

class DB:
    def __init__(self):
        self.conn = sqlite3.connect("shop.db", check_same_thread=False)
        self.cur = self.conn.cursor()

        self.cur.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, name TEXT, price INT, stock INT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, user_id TEXT, item TEXT, qty INT, roblox TEXT, price INT, status TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS points(user_id TEXT, point REAL)")
        self.conn.commit()
