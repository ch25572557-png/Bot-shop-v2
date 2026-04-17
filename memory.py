import sqlite3

class Memory:
    def __init__(self):
        self.conn = sqlite3.connect("shop.db")
        self.cur = self.conn.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            item TEXT,
            status TEXT
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS stock(
            name TEXT PRIMARY KEY,
            qty INTEGER,
            price REAL
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS points(
            user TEXT PRIMARY KEY,
            point INTEGER
        )
        """)

        # 🆕 เชื่อม ticket กับ order
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets(
            order_id INTEGER,
            channel_id TEXT
        )
        """)

        self.conn.commit()

    # 🆕 add order แบบคืน id
    def add_order(self, user, item, status="WAIT"):
        self.cur.execute(
            "INSERT INTO orders(user,item,status) VALUES(?,?,?)",
            (user, item, status)
        )
        self.conn.commit()
        return self.cur.lastrowid

    def update_order_status(self, order_id, status):
        self.cur.execute(
            "UPDATE orders SET status=? WHERE id=?",
            (status, order_id)
        )
        self.conn.commit()
