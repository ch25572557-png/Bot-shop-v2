import sqlite3

class Memory:
    def __init__(self):
        # 🟡 กัน thread crash (สำคัญสำหรับ discord bot)
        self.conn = sqlite3.connect("shop.db", check_same_thread=False)
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
            self.cur.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            )
            self.conn.commit()
        except Exception as e:
            print("[MEMORY] add column error:", e)

    # =====================
    # 📦 ORDER SYSTEM
    # =====================
    def add_order(self, user, item, amount=1, roblox_user=None, status="WAIT"):
        try:
            self.cur.execute(
                "INSERT INTO orders(user,item,amount,roblox_user,status) VALUES(?,?,?,?,?)",
                (user, item, amount, roblox_user, status)
            )
            self.conn.commit()
            return self.cur.lastrowid
        except Exception as e:
            print("[MEMORY] add_order error:", e)
            return None

    def get_order(self, order_id):
        try:
            self.cur.execute(
                "SELECT user, item, amount, roblox_user, status FROM orders WHERE id=?",
                (order_id,)
            )
            return self.cur.fetchone()
        except Exception as e:
            print("[MEMORY] get_order error:", e)
            return None

    def get_all_orders(self):
        try:
            self.cur.execute(
                "SELECT id, user, item, amount, roblox_user, status FROM orders"
            )
            return self.cur.fetchall()
        except Exception as e:
            print("[MEMORY] get_all_orders error:", e)
            return []

    def update_order_status(self, order_id, status):
        try:
            self.cur.execute(
                "UPDATE orders SET status=? WHERE id=?",
                (status, order_id)
            )
            self.conn.commit()
        except Exception as e:
            print("[MEMORY] update_order_status error:", e)

    # =====================
    # 🎫 TICKET SYSTEM
    # =====================
    def save_ticket(self, order_id, channel_id):
        try:
            self.cur.execute("""
            INSERT OR REPLACE INTO tickets(order_id, channel_id)
            VALUES(?, ?)
            """, (order_id, channel_id))
            self.conn.commit()
        except Exception as e:
            print("[MEMORY] save_ticket error:", e)

    def get_ticket(self, order_id):
        try:
            self.cur.execute(
                "SELECT channel_id FROM tickets WHERE order_id=?",
                (order_id,)
            )
            return self.cur.fetchone()
        except Exception as e:
            print("[MEMORY] get_ticket error:", e)
            return None

    def get_order_by_channel(self, channel_id):
        try:
            self.cur.execute(
                "SELECT order_id FROM tickets WHERE channel_id=?",
                (channel_id,)
            )
            result = self.cur.fetchone()
            return result[0] if result else None
        except Exception as e:
            print("[MEMORY] get_order_by_channel error:", e)
            return None

    # =====================
    # 📦 STOCK SYSTEM (ATOMIC SAFE)
    # =====================
    def minus_stock(self, item, amount=1):
        try:
            self.cur.execute(
                "UPDATE stock SET qty = qty - ? WHERE name=? AND qty >= ?",
                (amount, item, amount)
            )
            self.conn.commit()
            return self.cur.rowcount > 0
        except Exception as e:
            print("[STOCK] minus_stock error:", e)
            return False

    def get_stock(self, item):
        try:
            self.cur.execute(
                "SELECT qty FROM stock WHERE name=?",
                (item,)
            )
            result = self.cur.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print("[STOCK] get_stock error:", e)
            return 0

    # 🟢 LOW STOCK (C FEATURE)
    def get_low_stock_items(self, threshold=5):
        try:
            self.cur.execute(
                "SELECT name, qty FROM stock WHERE qty <= ?",
                (threshold,)
            )
            return self.cur.fetchall()
        except Exception as e:
            print("[STOCK] low_stock error:", e)
            return []

    # =====================
    # 💰 POINT SYSTEM
    # =====================
    def add_points(self, user, amount):
        try:
            self.cur.execute("""
                INSERT INTO points(user, point)
                VALUES(?, ?)
                ON CONFLICT(user)
                DO UPDATE SET point = point + ?
            """, (user, amount, amount))
            self.conn.commit()
        except Exception as e:
            print("[POINT] add_points error:", e)

    def get_points(self, user):
        try:
            self.cur.execute(
                "SELECT point FROM points WHERE user=?",
                (user,)
            )
            return self.cur.fetchone()
        except Exception as e:
            print("[POINT] get_points error:", e)
            return None
