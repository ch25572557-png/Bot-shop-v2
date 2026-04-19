import sqlite3
import threading


class Memory:

    def __init__(self):

        self.conn = sqlite3.connect(
            "shop.db",
            check_same_thread=False
        )

        self.lock = threading.RLock()

        with self.lock:
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA synchronous=NORMAL")

        # =====================
        # TABLES
        # =====================
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            item TEXT NOT NULL,
            amount INTEGER DEFAULT 1,
            roblox_user TEXT,
            status TEXT NOT NULL
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS stock(
            name TEXT PRIMARY KEY,
            qty INTEGER NOT NULL CHECK(qty >= 0),
            price REAL NOT NULL DEFAULT 0
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS points(
            user TEXT PRIMARY KEY,
            point INTEGER DEFAULT 0
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets(
            order_id INTEGER PRIMARY KEY,
            channel_id TEXT
        )
        """)

        self.conn.commit()

    # =====================
    # ORDER
    # =====================
    def add_order(self, user, item, amount=1, roblox_user=None, status="WAIT"):

        try:
            amount = max(int(amount), 1)
        except:
            amount = 1

        try:
            with self.lock:
                cur = self.conn.cursor()
                cur.execute(
                    "INSERT INTO orders(user,item,amount,roblox_user,status) VALUES(?,?,?,?,?)",
                    (user, item, amount, roblox_user, status)
                )
                self.conn.commit()
                return cur.lastrowid

        except Exception as e:
            print("[MEMORY] add_order error:", e)
            return None

    def get_order(self, order_id):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT user,item,amount,roblox_user,status FROM orders WHERE id=?",
                (order_id,)
            )
            return cur.fetchone()
        except:
            return None

    def get_all_orders(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM orders ORDER BY id DESC")
            return cur.fetchall()
        except:
            return []

    def update_order_status(self, order_id, status):
        try:
            with self.lock:
                self.conn.execute(
                    "UPDATE orders SET status=? WHERE id=?",
                    (status, order_id)
                )
                self.conn.commit()
        except Exception as e:
            print("[MEMORY] update_order error:", e)

    # 🔥 FIX สำคัญ (ใช้ตอนปิดห้อง)
    def get_order_by_channel(self, channel_id):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT order_id FROM tickets WHERE channel_id=?",
                (channel_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None
        except:
            return None

    # =====================
    # TICKET
    # =====================
    def save_ticket(self, order_id, channel_id):
        try:
            with self.lock:
                self.conn.execute("""
                INSERT OR REPLACE INTO tickets(order_id, channel_id)
                VALUES(?, ?)
                """, (order_id, channel_id))
                self.conn.commit()
        except Exception as e:
            print("[MEMORY] save_ticket error:", e)

    def get_ticket(self, order_id):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT channel_id FROM tickets WHERE order_id=?",
                (order_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None
        except:
            return None

    # =====================
    # STOCK
    # =====================
    def minus_stock(self, item, amount=1):

        try:
            amount = max(int(amount), 1)
        except:
            amount = 1

        try:
            with self.lock:
                cur = self.conn.cursor()

                cur.execute("SELECT qty FROM stock WHERE name=?", (item,))
                row = cur.fetchone()

                if not row or row[0] < amount:
                    return False

                cur.execute(
                    "UPDATE stock SET qty = qty - ? WHERE name=?",
                    (amount, item)
                )

                self.conn.commit()
                return True

        except Exception as e:
            print("[MEMORY] minus_stock error:", e)
            return False

    def add_stock(self, item, amount):

        try:
            amount = max(int(amount), 1)
        except:
            amount = 1

        try:
            with self.lock:
                cur = self.conn.cursor()

                cur.execute("SELECT qty FROM stock WHERE name=?", (item,))
                row = cur.fetchone()

                if row:
                    cur.execute(
                        "UPDATE stock SET qty = qty + ? WHERE name=?",
                        (amount, item)
                    )
                else:
                    cur.execute(
                        "INSERT INTO stock(name, qty, price) VALUES(?, ?, 0)",
                        (item, amount)
                    )

                self.conn.commit()

        except Exception as e:
            print("[MEMORY] add_stock error:", e)

    def get_stock(self, item):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT qty FROM stock WHERE name=?", (item,))
            row = cur.fetchone()
            return row[0] if row else 0
        except:
            return 0

    # =====================
    # POINTS (🔥 เพิ่มให้ครบ)
    # =====================
    def add_points(self, user, point):

        try:
            with self.lock:
                cur = self.conn.cursor()

                cur.execute(
                    "INSERT INTO points(user, point) VALUES(?, ?) "
                    "ON CONFLICT(user) DO UPDATE SET point = point + ?",
                    (user, point, point)
                )

                self.conn.commit()

        except Exception as e:
            print("[MEMORY] add_points error:", e)

    def get_points(self, user):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT point FROM points WHERE user=?", (user,))
            row = cur.fetchone()
            return row[0] if row else 0
        except:
            return 0
