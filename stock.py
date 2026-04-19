import asyncio
import discord


class StockSystem:

    def __init__(self, mem, brain, bot):
        self.mem = mem
        self.brain = brain
        self.bot = bot
        self.running = False

    # =====================
    # 📦 MINUS STOCK
    # =====================
    async def minus(self, item, amount=1):
        return await self.mem.minus_stock(item, amount)

    # =====================
    # ➕ ADD STOCK
    # =====================
    async def add(self, name, qty, price=0):

        try:
            name = str(name).strip()
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
        return await self.mem.get_stock(item)

    # =====================
    # 🚀 START LOOP
    # =====================
    def start(self):

        if self.running:
            return

        self.running = True
        self.bot.loop.create_task(self._loop())

        print("📦 STOCK MONITOR STARTED (V2 FIXED)")

    # =====================
    # 🔁 LOOP
    # =====================
    async def _loop(self):

        while self.running:
            try:
                await self.check_stock()
                await asyncio.sleep(10)

            except Exception as e:
                print("[STOCK LOOP ERROR]", e)
                await asyncio.sleep(5)

    # =====================
    # 🔍 CHECK STOCK (🔥 FIX สำคัญ)
    # =====================
    async def check_stock(self):

        try:
            items = await self.mem.get_all_stock()  # 🔥 ใช้ Memory เท่านั้น

        except Exception as e:
            print("[STOCK FETCH ERROR]", e)
            return

        for name, qty in items:
            if qty <= 5:
                await self.notify(name, qty)

    # =====================
    # 📢 NOTIFY
    # =====================
    async def notify(self, name, qty):

        try:
            channel_id = self.brain.channel("STOCK_ALERT")

            if not channel_id:
                return

            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)

            if not channel:
                return

            embed = discord.Embed(
                title="📦 Stock Alert",
                description=f"สินค้า `{name}` ใกล้หมด",
                color=0xffcc00
            )

            embed.add_field(name="คงเหลือ", value=str(qty), inline=False)

            await channel.send(embed=embed)

        except Exception as e:
            print("[STOCK NOTIFY ERROR]", e)
