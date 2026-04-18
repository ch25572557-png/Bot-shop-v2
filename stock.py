import threading
import time
import discord
import asyncio

class StockSystem:
    def __init__(self, mem, bot=None):
        self.mem = mem
        self.bot = bot
        self.lock = threading.Lock()
        self.running = False

    # =====================
    # 📦 MINUS STOCK
    # =====================
    def minus(self, item, amount=1):

        try:
            amount = max(int(amount), 1)
        except:
            amount = 1

        try:
            with self.lock:
                cur = self.mem.conn.cursor()

                cur.execute(
                    """
                    UPDATE stock
                    SET qty = qty - ?
                    WHERE name = ? AND qty >= ?
                    """,
                    (amount, item, amount)
                )

                self.mem.conn.commit()
                return cur.rowcount > 0

        except Exception as e:
            print("[STOCK] minus error:", e)
            return False

    # =====================
    # ➕ ADD STOCK
    # =====================
    def add(self, name, qty, price):

        try:
            name = str(name).strip()
            qty = int(qty)
            price = float(price)
        except:
            return False

        if not name or qty <= 0 or price < 0:
            return False

        try:
            with self.lock:
                cur = self.mem.conn.cursor()

                cur.execute(
                    "SELECT qty FROM stock WHERE name=?",
                    (name,)
                )
                result = cur.fetchone()

                if result:
                    cur.execute(
                        """
                        UPDATE stock
                        SET qty = qty + ?
                        WHERE name = ?
                        """,
                        (qty, name)
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO stock(name, qty, price)
                        VALUES(?,?,?)
                        """,
                        (name, qty, price)
                    )

                self.mem.conn.commit()
                return True

        except Exception as e:
            print("[STOCK] add error:", e)
            return False

    # =====================
    # 📊 GET STOCK
    # =====================
    def get(self, item):

        try:
            with self.lock:
                cur = self.mem.conn.cursor()
                cur.execute(
                    "SELECT qty FROM stock WHERE name=?",
                    (item,)
                )

                result = cur.fetchone()
                return result[0] if result else 0

        except Exception as e:
            print("[STOCK] get error:", e)
            return 0

    # =====================
    # 🚀 START LOOP (IMPORTANT)
    # =====================
    def start(self):
        if self.running:
            return

        self.running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

        print("📦 STOCK MONITOR STARTED")

    # =====================
    # 🔁 MONITOR LOOP
    # =====================
    def _loop(self):
        while self.running:
            try:
                with self.lock:
                    cur = self.mem.conn.cursor()
                    cur.execute("SELECT name, qty FROM stock")
                    items = cur.fetchall()

                for name, qty in items:

                    if qty <= 5:
                        self._notify(name, qty)

                time.sleep(10)

            except Exception as e:
                print("[STOCK LOOP ERROR]", e)
                time.sleep(5)

    # =====================
    # 📢 NOTIFY (EMBED)
    # =====================
    def _notify(self, name, qty):
        if not self.bot:
            return

        channel = None

        # หา channel ชื่อ stock-alert
        for c in self.bot.get_all_channels():
            if c.name == "stock-alert":
                channel = c
                break

        if not channel:
            return

        embed = discord.Embed(
            title="📦 Stock Alert",
            description=f"สินค้า `{name}` ใกล้หมดแล้ว",
            color=0xffcc00
        )

        embed.add_field(name="คงเหลือ", value=str(qty), inline=False)

        asyncio.create_task(channel.send(embed=embed))
