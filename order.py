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
        self.pending_ready = set()  # 🔥 NEW: ready-to-ship list
        self._started = False
        self._lock = asyncio.Lock()

    # =====================
    # 🚀 START
    # =====================
    async def start(self):
        if self._started:
            return

        self._started = True
        asyncio.create_task(self.farm_worker())
        print("🌾 FARM V3 STABLE ONLINE")

    # =====================
    # 📢 ADMIN
    # =====================
    async def send_admin(self, title, desc, color=0x00ffcc):

        try:
            ch_id = self.brain.channel("ORDER_NOTIFY")
            if not ch_id:
                return

            channel = self.bot.get_channel(ch_id) or await self.bot.fetch_channel(ch_id)

            if channel:
                await channel.send(embed=discord.Embed(
                    title=title,
                    description=desc,
                    color=color
                ))

        except Exception as e:
            print("[ADMIN ERROR]", e)

    # =====================
    # 📊 TICKET
    # =====================
    async def send_ticket(self, order_id, msg):

        try:
            channel_id = await self.mem.get_ticket(order_id)
            if not channel_id:
                return

            channel = self.bot.get_channel(int(channel_id)) or await self.bot.fetch_channel(int(channel_id))

            if channel:
                await channel.send(embed=discord.Embed(
                    title="📊 FARM STATUS",
                    description=msg,
                    color=0x3498db
                ))

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

        # 🔥 FARM QUEUE
        await self.farm_queue.put({
            "order_id": order_id,
            "guild": guild,
            "user": user,
            "item": item,
            "amount": amount,
            "roblox_user": roblox_user
        })

        await self.notify.admin(user, item, order_id)
        await self.backup.log(f"ORDER #{order_id} | {user} | {item} x{amount}")
        await self.ticket.create(guild, user, order_id)

        return order_id

    # =====================
    # 🌾 FARM WORKER (STABLE CORE)
    # =====================
    async def farm_worker(self):

        while True:
            try:
                task = await self.farm_queue.get()

                order_id = task["order_id"]
                item = task["item"]
                amount = task["amount"]

                await asyncio.sleep(2)

                # 🔥 FARM RESULT
                await self.mem.add_stock(item, amount)

                # 🔥 MARK READY
                await self.mem.update_order_status(order_id, "READY")

                self.pending_ready.add(order_id)

                await self.send_ticket(order_id, "🌾 ฟาร์มเสร็จแล้ว (READY)")

            except Exception as e:
                print("[FARM ERROR]", e)
                await asyncio.sleep(2)

    # =====================
    # ✅ COMPLETE (NO BLOCK, WAIT READY ONLY)
    # =====================
    async def complete(self, channel):

        order_id = await self.mem.get_order_by_channel(str(channel.id))
        if not order_id:
            return False

        if order_id in self.processing:
            return False

        self.processing.add(order_id)

        try:
            data = await self.mem.get_order(order_id)
            if not data:
                return False

            user, item, amount, roblox_user, status = data

            # 🔥 WAIT FARM ONLY
            if order_id not in self.pending_ready:
                await channel.send("⏳ กำลังฟาร์ม กรุณารอ...")
                return False

            self.pending_ready.discard(order_id)

            await self.mem.update_order_status(order_id, "DONE")

            point = int(self.brain.setting("POINT_PER_ORDER", 0))
            await self.mem.add_points(user, point)

            await self.notify.complete(user, item, order_id)
            await self.backup.complete(order_id, user, item)

            await self.send_ticket(order_id, "✅ ส่งของสำเร็จ")

            await channel.send(embed=discord.Embed(
                title="✅ DONE",
                description=f"{item} x{amount}\n+{point} points",
                color=0x00ff00
            ))

            await asyncio.sleep(2)

            try:
                fresh = self.bot.get_channel(channel.id) or await self.bot.fetch_channel(channel.id)
                if fresh:
                    await fresh.delete(reason=f"Order #{order_id}")

            except Exception as e:
                print("[DELETE ERROR]", e)

            return True

        finally:
            self.processing.discard(order_id)
