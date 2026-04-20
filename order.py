import asyncio
import discord

class OrderSystem:

    def __init__(self, mem, ticket, notify, backup, brain, bot):

        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup
        self.brain = brain
        self.bot = bot

        self.farm_queue = asyncio.Queue()

        self.processing = set()
        self.processing_orders = set()

        self._started = False
        self._lock = asyncio.Lock()

        # 🔥 ปรับจำนวน worker ได้
        self.worker_count = 3

    # =====================
    # 🚀 START SYSTEM
    # =====================
    async def start(self):
        if self._started:
            return

        self._started = True

        for _ in range(self.worker_count):
            asyncio.create_task(self.farm_worker())

        print(f"🌾 FARM WORKERS STARTED: {self.worker_count}")

    # =====================
    # 📊 TICKET UPDATE
    # =====================
    async def send_ticket(self, order_id, msg):

        try:
            channel_id = await self.mem.get_ticket(order_id)
            if not channel_id:
                return

            channel = self.bot.get_channel(int(channel_id)) or await self.bot.fetch_channel(int(channel_id))

            if channel:
                await channel.send(
                    embed=discord.Embed(
                        title="📊 STATUS",
                        description=msg,
                        color=0x3498db
                    )
                )

        except Exception as e:
            print("[TICKET ERROR]", e)

    # =====================
    # 🛒 CREATE ORDER
    # =====================
    async def create(self, guild, user, item, amount=1, roblox_user=None):

        amount = max(int(amount or 1), 1)
        item = str(item).strip().lower()

        order_id = await self.mem.add_order(
            str(user),
            item,
            amount,
            roblox_user,
            "PENDING"
        )

        if not order_id:
            return False

        # 🔥 เช็ค stock ก่อน
        stock = await self.mem.get_stock(item)

        if stock >= amount:
            await self.mem.update_order_status(order_id, "READY")
            await self.send_ticket(order_id, "📦 ของพร้อมส่ง")
        else:
            await self.mem.update_order_status(order_id, "FARMING")

            await self.farm_queue.put({
                "order_id": order_id,
                "item": item,
                "amount": amount
            })

        await self.notify.admin(user, item, order_id)
        await self.backup.log(f"ORDER #{order_id} | {user} | {item} x{amount}")
        await self.ticket.create(guild, user, order_id)

        return order_id

    # =====================
    # ✅ COMPLETE ORDER
    # =====================
    async def complete(self, channel):

        order_id = await self.mem.get_order_by_channel(str(channel.id))
        if not order_id:
            return False

        if order_id in self.processing:
            return False

        self.processing.add(order_id)

        try:
            async with self._lock:

                data = await self.mem.get_order(order_id)
                if not data:
                    return False

                user, item, amount, roblox_user, status = data
                item = item.lower().strip()

                if status != "READY":
                    await channel.send("❌ ยังไม่พร้อมส่ง")
                    return False

                # 🔥 atomic stock
                ok = await self.mem.minus_stock(item, amount)

                if not ok:
                    await channel.send("❌ stock ไม่พอ")
                    return False

                await self.mem.update_order_status(order_id, "DONE")

                point = int(self.brain.setting("POINT_PER_ORDER", 0))
                await self.mem.add_points(user, point)

                await self.notify.complete(user, item, order_id)
                await self.backup.complete(order_id, user, item)

                await self.send_ticket(order_id, "✅ ส่งของแล้ว")

                await channel.send(
                    embed=discord.Embed(
                        title="✅ DONE",
                        description=f"{item} x{amount}\n+{point} points",
                        color=0x00ff00
                    )
                )

                await asyncio.sleep(2)

                try:
                    fresh = self.bot.get_channel(channel.id) or await self.bot.fetch_channel(channel.id)
                    if fresh:
                        await fresh.delete(reason=f"Order #{order_id} completed")
                except Exception as e:
                    print("[DELETE ERROR]", e)

                return True

        finally:
            self.processing.discard(order_id)

    # =====================
    # 🌾 FARM WORKER (PRODUCTION)
    # =====================
    async def farm_worker(self):

        while True:
            try:
                try:
                    task = await asyncio.wait_for(self.farm_queue.get(), timeout=3)

                    order_id = task["order_id"]
                    item = task["item"]
                    amount = task["amount"]

                except asyncio.TimeoutError:
                    # 🔥 fallback จาก DB
                    rows = await self.mem.get_pending_farm(5)

                    if not rows:
                        await asyncio.sleep(2)
                        continue

                    order_id, item, amount = rows[0]

                # 🔒 กันซ้ำ
                if order_id in self.processing_orders:
                    continue

                self.processing_orders.add(order_id)

                try:
                    await asyncio.sleep(2)

                    await self.mem.add_stock(item, amount)
                    await self.mem.update_order_status(order_id, "READY")

                    await self.send_ticket(order_id, "🌾 ฟาร์มเสร็จแล้ว พร้อมส่ง")

                finally:
                    self.processing_orders.discard(order_id)

            except Exception as e:
                print("[FARM ERROR]", e)
                await asyncio.sleep(2)
