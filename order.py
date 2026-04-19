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
        self._started = False

        self.processing = set()
        self._lock = asyncio.Lock()

    # =====================
    # 🚀 START SYSTEM
    # =====================
    async def start(self):
        if self._started:
            return

        self._started = True
        asyncio.create_task(self.farm_worker())
        print("🌾 FARM V3 STABLE STARTED")

    # =====================
    # 📢 ADMIN NOTIFY
    # =====================
    async def send_admin(self, title, desc, color=0x00ffcc):

        try:
            ch_id = self.brain.channel("ORDER_NOTIFY")
            if not ch_id:
                return

            channel = self.bot.get_channel(ch_id) or await self.bot.fetch_channel(ch_id)

            if channel:
                embed = discord.Embed(
                    title=title,
                    description=desc,
                    color=color
                )
                await channel.send(embed=embed)

        except Exception as e:
            print("[ADMIN SEND ERROR]", e)

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
                embed = discord.Embed(
                    title="📊 FARM STATUS",
                    description=msg,
                    color=0x3498db
                )
                await channel.send(embed=embed)

        except Exception as e:
            print("[TICKET ERROR]", e)

    # =====================
    # 🛒 CREATE ORDER (QUEUE ONLY)
    # =====================
    async def create(self, guild, user, item, amount=1, roblox_user=None):

        try:
            amount = max(int(amount), 1)
        except:
            amount = 1

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

        # =====================
        # 🌾 PUSH TO FARM QUEUE (NO VIP / NO PRIORITY)
        # =====================
        await self.farm_queue.put({
            "order_id": order_id,
            "guild": guild,
            "user": user,
            "item": item,
            "amount": amount,
            "roblox_user": roblox_user
        })

        await self.mem.update_order_status(order_id, "QUEUED")

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
            data = await self.mem.get_order(order_id)
            if not data:
                return False

            user, item, amount, roblox_user, status = data
            item = item.lower().strip()

            if status != "FARMED":
                await channel.send("❌ ยังฟาร์มไม่เสร็จ")
                return False

            # =====================
            # 🔥 FINAL STOCK CHECK (SAFETY ONLY)
            # =====================
            ok = await self.mem.minus_stock(item, amount)

            if not ok:
                await channel.send("❌ สต๊อกไม่พอ")
                return False

            await self.mem.update_order_status(order_id, "DONE")

            point = int(self.brain.setting("POINT_PER_ORDER", 0))
            await self.mem.add_points(user, point)

            await self.notify.complete(user, item, order_id)
            await self.backup.complete(order_id, user, item)

            await self.send_ticket(order_id, "✅ ส่งของเสร็จแล้ว")

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
    # 🌾 FARM WORKER V3 STABLE CORE
    # =====================
    async def farm_worker(self):

        while True:
            try:
                task = await self.farm_queue.get()

                order_id = task["order_id"]
                item = task["item"]
                amount = task["amount"]

                # =====================
                # 🌾 MARK FARMING
                # =====================
                await self.mem.update_order_status(order_id, "FARMING")

                await self.send_ticket(order_id, "🌾 กำลังฟาร์มสินค้า...")

                # =====================
                # ⏳ SIMULATE FARM TIME
                # =====================
                await asyncio.sleep(2)

                # =====================
                # 📦 ADD STOCK
                # =====================
                await self.mem.add_stock(item, amount)

                # =====================
                # 🌾 MARK FARMED
                # =====================
                await self.mem.update_order_status(order_id, "FARMED")

                await self.send_ticket(order_id, "🌾 ฟาร์มเสร็จแล้ว")

            except Exception as e:
                print("[FARM ERROR]", e)
                await asyncio.sleep(2)
