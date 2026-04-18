import sqlite3

class Memory:
    def __init__(self):
        self.conn = sqlite3.connect("shop.db")
        self.cur = self.conn.cursor()

        # =====================
        # 📦 ORDERS
        # =====================
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            item TEXT,
            status TEXT
        )
        """)

        # 🆕 เพิ่ม column แบบไม่พัง DB เดิม
        self._safe_add_column("orders", "amount", "INTEGER DEFAULT 1")
        self._safe_add_column("orders", "roblox_user", "TEXT")

        # =====================
        # 📦 STOCK
        # =====================
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS stock(
            name TEXT PRIMARY KEY,
            qty INTEGER,
            price REAL
        )
        """)

        # =====================
        # 💰 POINTS
        # =====================
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS points(
            user TEXT PRIMARY KEY,
            point INTEGER
        )
        """)

        # =====================
        # 🎫 TICKETS
        # =====================
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets(
            order_id INTEGER PRIMARY KEY,
            channel_id TEXT
        )
        """)

        self.conn.commit()

    # =====================
    # 🛠 SAFE ADD COLUMN
    # =====================
    def _safe_add_column(self, table, column, definition):
        try:
            self.cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            self.conn.commit()
        except:
            pass  # มีอยู่แล้วจะ error → ข้าม

    # =====================
    # 📦 ORDER SYSTEM
    # =====================

    def add_order(self, user, item, amount=1, roblox_user=None, status="WAIT"):
        self.cur.execute(
            "INSERT INTO orders(user,item,amount,roblox_user,status) VALUES(?,?,?,?,?)",
            (user, item, amount, roblox_user, status)
        )
        self.conn.commit()
        return self.cur.lastrowid

    def get_order(self, order_id):
        self.cur.execute(
            "SELECT user, item, amount, roblox_user, status FROM orders WHERE id=?",
            (order_id,)
        )
        return self.cur.fetchone()

    def get_all_orders(self):
        self.cur.execute(
            "SELECT id, user, item, amount, roblox_user, status FROM orders"
        )
        return self.cur.fetchall()

    def update_order_status(self, order_id, status):
        self.cur.execute(
            "UPDATE orders SET status=? WHERE id=?",
            (status, order_id)
        )
        self.conn.commit()

    # =====================
    # 🎫 TICKET SYSTEM
    # =====================

    def save_ticket(self, order_id, channel_id):
        self.cur.execute("""
        INSERT OR REPLACE INTO tickets(order_id, channel_id)
        VALUES(?, ?)
        """, (order_id, channel_id))
        self.conn.commit()

    def get_ticket(self, order_id):
        self.cur.execute(
            "SELECT channel_id FROM tickets WHERE order_id=?",
            (order_id,)
        )
        return self.cur.fetchone()

    def get_order_by_channel(self, channel_id):
        self.cur.execute(
            "SELECT order_id FROM tickets WHERE channel_id=?",
            (channel_id,)
        )
        result = self.cur.fetchone()
        return result[0] if result else None

    # =====================
    # 📦 STOCK SYSTEM
    # =====================

    def minus_stock(self, item, amount=1):
        self.cur.execute(
            "SELECT qty FROM stock WHERE name=?",
            (item,)
        )
        result = self.cur.fetchone()

        if not result:
            return False

        qty = result[0]

        if qty < amount:
            return False

        self.cur.execute(
            "UPDATE stock SET qty = qty - ? WHERE name=?",
            (amount, item)
        )
        self.conn.commit()
        return True

    # =====================
    # 💰 POINT SYSTEM
    # =====================

    def add_points(self, user, amount):
        self.cur.execute(
            "INSERT INTO points(user, point) VALUES(?, ?) "
            "ON CONFLICT(user) DO UPDATE SET point = point + ?",
            (user, amount, amount)
        )
        self.conn.commit()

    def get_points(self, user):
        self.cur.execute(
            "SELECT point FROM points WHERE user=?",
            (user,)
        )
        return self.cur.fetchone()
