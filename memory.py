import sqlite3

class Memory:
    def __init__(self):
        self.conn = sqlite3.connect("shop.db")
        self.cur = self.conn.cursor()

        self.cur.execute("CREATE TABLE IF NOT EXISTS orders(user,item,status)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS stock(name,qty,price)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS points(user,point)")
