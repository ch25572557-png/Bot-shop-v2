import sqlite3
import threading

class Memory:
    def __init__(self):

        self.conn = sqlite3.connect(
            "shop.db",
            check_same_thread=False
        )

        self.lock = threading.Lock()

        # =====================
        # ⚙️ DB SAFE MODE
        # =====================
        with self.lock:
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA synchronous=NORMAL")

        # =====================
        # 📦 ORDERS
        # =====================
        with self.lock:
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

        # =====================
        # 📦 STOCK
        # =====================
        with self.lock:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS stock(
                name TEXT PRIMARY KEY,
                qty INTEGER NOT NULL CHECK(qty >= 0),
                price REAL NOT NULL
            )
            """)

        # =====================
        # 💰 POINTS
        # =====================
        with self.lock:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS points(
                user TEXT PRIMARY KEY,
                point INTEGER DEFAULT 0
            )
            """)

        # =====================
        # 🎫 TICKETS
        # =====================
        with self.lock:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets(
                order_id INTEGER PRIMARY KEY,
                channel_id TEXT
            )
            """)

        self.conn.commit()

    # =====================
    # 📦 ORDER SYSTEM
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
            cur.execute(
                "SELECT id,user,item,amount,roblox_user,status FROM orders"
            )
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
        except:
            pass

    # =====================
    # 🎫 TICKET
    # =====================
    def save_ticket(self, order_id, channel_id):
        try:
            with self.lock:
                self.conn.execute("""
                INSERT OR REPLACE INTO tickets(order_id, channel_id)
                VALUES(?, ?)
                """, (order_id, channel_id))
                self.conn.commit()
        except:
            pass

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
    # 📦 STOCK (SAFE + FARM READY)
    # =====================
    def minus_stock(self, item, amount=1):

        try:
            amount = max(int(amount), 1)
        except:
            amount = 1

        try:
            with self.lock:
                cur = self.conn.cursor()

                # 🔴 SAFE: กันติดลบ
                cur.execute(
                    "UPDATE stock SET qty = qty - ? WHERE name=? AND qty >= ?",
                    (amount, item, amount)
                )

                self.conn.commit()

                return cur.rowcount > 0

        except:
            return False

    def add_stock(self, item, amount):

        try:
            amount = max(int(amount), 1)
        except:
            amount = 1

        try:
            with self.lock:
                self.conn.execute("""
                    INSERT INTO stock(name, qty, price)
                    VALUES(?, ?, 0)
                    ON CONFLICT(name)
                    DO UPDATE SET qty = qty + ?
                """, (item, amount, amount))

                self.conn.commit()

        except:
            pass

    def get_stock(self, item):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT qty FROM stock WHERE name=?",
                (item,)
            )
            row = cur.fetchone()
            return row[0] if row else 0
        except:
            return 0

    # =====================
    # 💰 POINTS
    # =====================
    def add_points(self, user, amount):
        try:
            with self.lock:
                self.conn.execute("""
                    INSERT INTO points(user,point)
                    VALUES(?,?)
                    ON CONFLICT(user)
                    DO UPDATE SET point = point + ?
                """, (user, amount, amount))
                self.conn.commit()
        except:
            pass

    def get_points(self, user):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT point FROM points WHERE user=?",
                (user,)
            )
            row = cur.fetchone()
            return row[0] if row else 0
        except:
            return 0
