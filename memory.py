import aiosqlite
import asyncio


class Memory:

    def __init__(self):
        self.db_path = "shop.db"
        self.db = None
        self.lock = asyncio.Lock()

    async def init(self):

        self.db = await aiosqlite.connect(self.db_path)

        # 🔥 PERFORMANCE + STABILITY
        await self.db.execute("PRAGMA journal_mode=WAL")
        await self.db.execute("PRAGMA synchronous=NORMAL")
        await self.db.execute("PRAGMA busy_timeout=5000")

        # =====================
        # 📦 TABLES
        # =====================
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            item TEXT NOT NULL,
            amount INTEGER DEFAULT 1,
            roblox_user TEXT,
            status TEXT NOT NULL
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS stock(
            name TEXT PRIMARY KEY,
            qty INTEGER NOT NULL CHECK(qty >= 0),
            price REAL NOT NULL DEFAULT 0
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS points(
            user TEXT PRIMARY KEY,
            point INTEGER DEFAULT 0
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS tickets(
            order_id INTEGER PRIMARY KEY,
            channel_id TEXT
        )
        """)

        # 🔥 INDEX
        await self.db.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        await self.db.execute("CREATE INDEX IF NOT EXISTS idx_tickets_channel ON tickets(channel_id)")

        await self.db.commit()

    # =====================
    # ⚙️ EXEC SAFE (FIXED)
    # =====================
    async def execute(self, query, params=(), fetch=False, one=False):

        async with self.lock:
            try:
                cur = await self.db.execute(query, params)

                if one:
                    row = await cur.fetchone()
                    await cur.close()
                    return row

                if fetch:
                    rows = await cur.fetchall()
                    await cur.close()
                    return rows

                await self.db.commit()
                await cur.close()
                return None

            except Exception as e:
                print("[DB ERROR]", e)
                return None

    # =====================
    # 🛒 ORDER
    # =====================
    async def add_order(self, user, item, amount=1, roblox_user=None, status="PENDING"):

        amount = max(int(amount or 1), 1)

        # ❌ ไม่ใช้ lock ซ้อน
        cur = await self.db.execute(
            "INSERT INTO orders(user,item,amount,roblox_user,status) VALUES(?,?,?,?,?)",
            (user, item, amount, roblox_user, status)
        )
        await self.db.commit()
        return cur.lastrowid

    async def get_order(self, order_id):
        return await self.execute(
            "SELECT user,item,amount,roblox_user,status FROM orders WHERE id=?",
            (order_id,),
            one=True
        )

    async def update_order_status(self, order_id, status):
        await self.execute(
            "UPDATE orders SET status=? WHERE id=?",
            (status, order_id)
        )

    async def get_pending_farm(self, limit=10):
        return await self.execute(
            "SELECT id,item,amount FROM orders WHERE status='FARMING' LIMIT ?",
            (limit,),
            fetch=True
        )

    async def get_order_by_channel(self, channel_id):

        row = await self.execute(
            "SELECT order_id FROM tickets WHERE channel_id=?",
            (str(channel_id),),
            one=True
        )

        return row[0] if row else None

    # =====================
    # 🎫 TICKET
    # =====================
    async def save_ticket(self, order_id, channel_id):

        await self.execute(
            "INSERT OR REPLACE INTO tickets(order_id, channel_id) VALUES(?,?)",
            (order_id, str(channel_id))
        )

    async def get_ticket(self, order_id):

        row = await self.execute(
            "SELECT channel_id FROM tickets WHERE order_id=?",
            (order_id,),
            one=True
        )

        return int(row[0]) if row else None

    # =====================
    # 📦 STOCK
    # =====================
    def _norm(self, item):
        return str(item).strip().lower()

    async def minus_stock(self, item, amount=1):

        item = self._norm(item)
        amount = max(int(amount or 1), 1)

        async with self.lock:
            cur = await self.db.execute(
                "UPDATE stock SET qty = qty - ? WHERE name=? AND qty >= ?",
                (amount, item, amount)
            )
            await self.db.commit()
            return cur.rowcount > 0

    async def add_stock(self, item, amount):

        item = self._norm(item)
        amount = max(int(amount or 1), 1)

        await self.execute("""
        INSERT INTO stock(name,qty,price)
        VALUES(?,?,0)
        ON CONFLICT(name)
        DO UPDATE SET qty = qty + ?
        """, (item, amount, amount))

    async def get_stock(self, item):

        item = self._norm(item)

        row = await self.execute(
            "SELECT qty FROM stock WHERE name=?",
            (item,),
            one=True
        )

        return int(row[0]) if row else 0

    async def get_all_stock(self):
        return await self.execute(
            "SELECT name,qty FROM stock",
            fetch=True
        ) or []

    # =====================
    # 💰 POINTS
    # =====================
    async def add_points(self, user, point):

        await self.execute("""
        INSERT INTO points(user, point)
        VALUES(?,?)
        ON CONFLICT(user)
        DO UPDATE SET point = point + ?
        """, (user, point, point))

    async def get_points(self, user):

        row = await self.execute(
            "SELECT point FROM points WHERE user=?",
            (user,),
            one=True
        )

        return int(row[0]) if row else 0

    # =====================
    # 🔌 CLOSE (OPTIONAL)
    # =====================
    async def close(self):
        if self.db:
            await self.db.close()
