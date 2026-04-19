import aiosqlite
import asyncio


class Memory:

    def __init__(self):
        self.db_path = "shop.db"
        self.lock = asyncio.Lock()

    # =====================
    # 🚀 INIT
    # =====================
    async def init(self):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA synchronous=NORMAL")

            await db.execute("""
            CREATE TABLE IF NOT EXISTS orders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                item TEXT NOT NULL,
                amount INTEGER DEFAULT 1,
                roblox_user TEXT,
                status TEXT NOT NULL
            )
            """)

            await db.execute("""
            CREATE TABLE IF NOT EXISTS stock(
                name TEXT PRIMARY KEY,
                qty INTEGER NOT NULL CHECK(qty >= 0),
                price REAL NOT NULL DEFAULT 0
            )
            """)

            await db.execute("""
            CREATE TABLE IF NOT EXISTS points(
                user TEXT PRIMARY KEY,
                point INTEGER DEFAULT 0
            )
            """)

            await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets(
                order_id INTEGER PRIMARY KEY,
                channel_id TEXT
            )
            """)

            await db.commit()

    # =====================
    # 🛒 ORDER
    # =====================
    async def add_order(self, user, item, amount=1, roblox_user=None, status="WAIT"):

        amount = max(int(amount or 1), 1)

        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:

                cur = await db.execute(
                    "INSERT INTO orders(user,item,amount,roblox_user,status) VALUES(?,?,?,?,?)",
                    (user, item, amount, roblox_user, status)
                )

                await db.commit()
                return cur.lastrowid

    async def get_order(self, order_id):

        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "SELECT user,item,amount,roblox_user,status FROM orders WHERE id=?",
                (order_id,)
            )
            return await cur.fetchone()

    async def update_order_status(self, order_id, status):

        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE orders SET status=? WHERE id=?",
                    (status, order_id)
                )
                await db.commit()

    async def get_order_by_channel(self, channel_id):

        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "SELECT order_id FROM tickets WHERE channel_id=?",
                (channel_id,)
            )
            row = await cur.fetchone()
            return row[0] if row else None

    # =====================
    # 🎫 TICKET
    # =====================
    async def save_ticket(self, order_id, channel_id):

        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO tickets(order_id, channel_id) VALUES(?,?)",
                    (order_id, channel_id)
                )
                await db.commit()

    async def get_ticket(self, order_id):

        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "SELECT channel_id FROM tickets WHERE order_id=?",
                (order_id,)
            )
            row = await cur.fetchone()
            return row[0] if row else None

    # =====================
    # 📦 STOCK (TRANSACTION SAFE)
    # =====================
    async def minus_stock(self, item, amount=1):

        amount = max(int(amount or 1), 1)

        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:

                cur = await db.execute(
                    "SELECT qty FROM stock WHERE name=?",
                    (item,)
                )
                row = await cur.fetchone()

                if not row or row[0] < amount:
                    return False

                await db.execute(
                    "UPDATE stock SET qty = qty - ? WHERE name=?",
                    (amount, item)
                )

                await db.commit()
                return True

    async def add_stock(self, item, amount):

        amount = max(int(amount or 1), 1)

        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:

                cur = await db.execute(
                    "SELECT qty FROM stock WHERE name=?",
                    (item,)
                )
                row = await cur.fetchone()

                if row:
                    await db.execute(
                        "UPDATE stock SET qty = qty + ? WHERE name=?",
                        (amount, item)
                    )
                else:
                    await db.execute(
                        "INSERT INTO stock(name, qty, price) VALUES(?, ?, 0)",
                        (item, amount)
                    )

                await db.commit()

    async def get_stock(self, item):

        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "SELECT qty FROM stock WHERE name=?",
                (item,)
            )
            row = await cur.fetchone()
            return row[0] if row else 0

    # =====================
    # 💰 POINTS
    # =====================
    async def add_points(self, user, point):

        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:

                await db.execute(
                    "INSERT INTO points(user, point) VALUES(?, ?) "
                    "ON CONFLICT(user) DO UPDATE SET point = point + ?",
                    (user, point, point)
                )

                await db.commit()

    async def get_points(self, user):

        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "SELECT point FROM points WHERE user=?",
                (user,)
            )
            row = await cur.fetchone()
            return row[0] if row else 0
