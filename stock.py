import asyncio
import discord


class StockSystem:

    def __init__(self, mem, brain, bot, notify):
        self.mem = mem
        self.brain = brain
        self.bot = bot
        self.notify = notify  # 🔥 FIX สำคัญ
        self.running = False

    # =====================
    # 📦 MINUS STOCK
    # =====================
    async def minus(self, item, amount=1):
        item = str(item).strip().lower()
        return await self.mem.minus_stock(item, amount)

    # =====================
    # ➕ ADD STOCK
    # =====================
    async def add(self, name, qty, price=0):

        try:
            name = str(name).strip().lower()
            qty = int(qty)
        except:
            return False

        if not name or qty <= 0:
            return False

        await self.mem.add_stock(name, qty)
        return True

    # =====================
    # 📊 GET STOCK
    # =====================
    async def get(self, item):
        item = str(item).strip().lower()
        return await self.mem.get_stock(item)

    # =====================
    # 🚀 START LOOP (FIXED)
    # =====================
    def start(self):

        if self.running:
            return

        self.running = True

        # 🔥 FIX: safe async task
        asyncio.create_task(self._loop())

        print("📦 STOCK MONITOR STARTED")

    # =====================
    # 🔁 LOOP
    # =====================
    async def _loop(self):

        await self.bot.wait_until_ready()

        while self.running:
            try:
                await self.check_stock()
                await asyncio.sleep(10)

            except Exception as e:
                print("[STOCK LOOP ERROR]", e)
                await asyncio.sleep(5)

    # =====================
    # 🔍 CHECK STOCK
    # =====================
    async def check_stock(self):

        try:
            items = await self.mem.get_all_stock()
        except Exception as e:
            print("[STOCK FETCH ERROR]", e)
            return

        if not items:
            return

        for name, qty in items:
            if qty <= 5:
                await self.notify_low_stock(name, qty)

    # =====================
    # 📢 NOTIFY (FIXED NAME)
    # =====================
    async def notify_low_stock(self, name, qty):

        try:
            channel_id = self.brain.channel("STOCK_ALERT")
            if not channel_id:
                return

            channel_id = int(channel_id)

            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)

            if not channel:
                return

            embed = discord.Embed(
                title="📦 Stock Alert",
                description=f"สินค้า `{name}` ใกล้หมด",
                color=0xffcc00
            )

            embed.add_field(name="คงเหลือ", value=str(qty), inline=False)

            await self.notify.stock_alert(name, qty)  # 🔥 ใช้ระบบ notify จริง
            await channel.send(embed=embed)

        except Exception as e:
            print("[STOCK NOTIFY ERROR]", e)
