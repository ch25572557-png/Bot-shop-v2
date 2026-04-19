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
    # 📢 ADMIN SEND (FIX KEY)
    # =====================
    async def send_admin(self, title, desc, color=0x00ffcc):

        try:
            ch_id = self.brain.channel("ORDER_NOTIFY")  # 🔥 FIX
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
    # 📢 TICKET UPDATE
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
            print("[TICKET ERROR]", e)

    # =====================
    # 🛒 CREATE ORDER
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
            "PENDING"
        )

        if not order_id:
            return False

        # 🔥 ใช้ notify ตัวเดียวพอ (ไม่ต้อง send_admin ซ้ำ)
        await self.notify.admin(user, item, order_id)

        await self.backup.log(f"ORDER #{order_id} | {user} | {item} x{amount}")
        await self.ticket.create(guild, user, order_id)

        return order_id

    # =====================
    # ✅ COMPLETE ORDER (FINAL FIX)
    # =====================
    async def complete(self, channel):

        print(f"[DEBUG] complete() called for channel {channel.id}")

        order_id = self.mem.get_order_by_channel(str(channel.id))
        if not order_id:
            print("[DEBUG] No order found")
            return False

        if order_id in self.processing:
            print("[DEBUG] Already processing")
            return False

        self.processing.add(order_id)

        try:
            data = self.mem.get_order(order_id)
            if not data:
                print("[DEBUG] Order not found")
                return False

            user, item, amount, roblox_user, status = data

            if status == "DONE":
                print("[DEBUG] Already DONE")
                return False

            # =====================
            # 🔥 STOCK
            # =====================
            if not self.mem.minus_stock(item, amount):
                await channel.send("❌ สต๊อกไม่พอ")
                return False

            # =====================
            # STATUS
            # =====================
            self.mem.update_order_status(order_id, "DONE")

            point = int(self.brain.setting("POINT_PER_ORDER", 0))
            self.mem.add_points(user, point)

            # =====================
            # NOTIFY (🔥 FIX)
            # =====================
            await self.notify.complete(user, item, order_id)

            await self.backup.complete(order_id, user, item)

            # =====================
            # TICKET
            # =====================
            await self.send_ticket(order_id, "✅ ส่งของเสร็จแล้ว")

            # =====================
            # USER
            # =====================
            await channel.send(
                embed=discord.Embed(
                    title="✅ DONE",
                    description=f"{item} x{amount}\n+{point} points",
                    color=0x00ff00
                )
            )

            # =====================
            # 🔒 DELETE CHANNEL (ULTRA SAFE)
            # =====================
            await asyncio.sleep(2)

            try:
                fresh = self.bot.get_channel(channel.id)

                if not fresh:
                    fresh = await self.bot.fetch_channel(channel.id)

                if not fresh:
                    print("[DELETE] channel missing")
                    return False

                await fresh.delete(reason=f"Order #{order_id} completed")
                print(f"[SUCCESS] deleted {channel.id}")

            except discord.Forbidden:
                print("[DELETE ERROR] ไม่มี permission (Manage Channels)")

            except discord.NotFound:
                print("[DELETE ERROR] channel หายไปแล้ว")

            except Exception as e:
                print("[DELETE ERROR]", e)

            return True

        finally:
            self.processing.discard(order_id)

    # =====================
    # 🧠 FARM
    # =====================
    async def farm_worker(self):

        while True:
            try:
                task = await self.farm_queue.get()
                await asyncio.sleep(2)

                self.mem.add_stock(task["item"], task["amount"])

            except Exception as e:
                print("[FARM ERROR]", e)
                await asyncio.sleep(2)
