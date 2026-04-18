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

        self._lock = asyncio.Lock()
        self.farm_queue = asyncio.Queue()
        self._started = False
        self.processing = set()

    # =====================
    # 🚀 START
    # =====================
    async def start(self):
        if self._started:
            return
        self._started = True
        asyncio.create_task(self.farm_worker())

    # =====================
    # 📢 ADMIN (EMBED FIX)
    # =====================
    async def send_admin(self, title, desc, color=0x00ffcc):
        try:
            ch_id = self.brain.get("CHANNELS.ORDER_NOTIFY")
            if not ch_id:
                return

            channel = self.bot.get_channel(int(ch_id)) or await self.bot.fetch_channel(int(ch_id))

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
    # 📢 TICKET (EMBED FIX)
    # =====================
    async def send_ticket(self, order_id, msg):
        try:
            channel_id = self.mem.get_ticket(order_id)
            if not channel_id:
                return

            channel = self.bot.get_channel(int(channel_id)) or await self.bot.fetch_channel(int(channel_id))

            if channel:
                embed = discord.Embed(
                    title="📊 STATUS UPDATE",
                    description=msg,
                    color=0x3498db
                )
                await channel.send(embed=embed)

        except Exception as e:
            print("[TICKET STATUS ERROR]", e)

    # =====================
    # 🛒 CREATE ORDER (EMBED FIX)
    # =====================
    async def create(self, guild, user, item, amount=1, roblox_user=None):

        try:
            amount = max(int(amount), 1)
        except:
            amount = 1

        order_id = self.mem.add_order(
            str(user),
            item,
            amount,
            roblox_user,
            "WAIT"
        )

        if not order_id:
            return False

        await self.send_admin(
            "📦 NEW ORDER",
            f"**Order ID:** #{order_id}\n"
            f"👤 User: {user}\n"
            f"📦 Item: {item} x{amount}",
            0x00ffcc
        )

        await self.notify.admin(user, item, order_id)
        await self.backup.log(f"ORDER #{order_id} | {user} | {item} x{amount}")
        await self.ticket.create(guild, user, order_id)

        return order_id

    # =====================
    # ✅ COMPLETE ORDER
    # =====================
    async def complete(self, channel):

        order_id = self.mem.get_order_by_channel(str(channel.id))
        if not order_id:
            return False

        if order_id in self.processing:
            return False

        self.processing.add(order_id)

        try:
            data = self.mem.get_order(order_id)
            if not data:
                return False

            user, item, amount, roblox_user, status = data

            if status == "DONE":
                return False

            async with self._lock:
                success = self.mem.minus_stock(item, amount)

            if not success:
                await channel.send("❌ สต๊อกไม่พอ")
                return False

            self.mem.update_order_status(order_id, "DONE")

            point = int(self.brain.get("SETTINGS.POINT_PER_ORDER") or 0)
            self.mem.add_points(user, point)

            # =====================
            # 📢 ADMIN EMBED
            # =====================
            await self.send_admin(
                "✅ ORDER COMPLETED",
                f"Order #{order_id}\n📦 {item} x{amount}\n💰 +{point} points",
                0x00ff00
            )

            # =====================
            # 📢 TICKET EMBED
            # =====================
            await self.send_ticket(order_id, "✅ ส่งของเสร็จแล้ว")

            # =====================
            # 👤 CHANNEL RESPONSE
            # =====================
            embed = discord.Embed(
                title="✅ DONE",
                description=f"{item} x{amount}\n💰 +{point} points",
                color=0x00ff00
            )
            await channel.send(embed=embed)

            # =====================
            # 🔒 CLOSE CHANNEL
            # =====================
            await asyncio.sleep(3)
            await channel.delete(reason="Order completed")

            return True

        finally:
            self.processing.discard(order_id)

    # =====================
    # 🧠 FARM WORKER
    # =====================
    async def farm_worker(self):
        while True:
            try:
                task = await self.farm_queue.get()
                await asyncio.sleep(3)

                cur = self.mem.conn.cursor()
                cur.execute(
                    "UPDATE stock SET qty = qty + ? WHERE name=?",
                    (task["amount"], task["item"])
                )
                self.mem.conn.commit()

            except Exception as e:
                print("[FARM ERROR]", e)
                await asyncio.sleep(2)
