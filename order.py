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

        self.processing = set()
        self._lock = asyncio.Lock()

        self.farm_manager = None

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
    # 🛒 CREATE ORDER (ไม่ผูก stock แล้ว)
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

        # 🔥 ไม่เช็ค stock แล้ว → ไป FARMING ตรง
        await self.mem.update_order_status(order_id, "FARMING")

        if self.farm_manager:
            await self.farm_manager.add_job(order_id, item, amount)

        await self.notify.admin(user, item, order_id)
        await self.backup.log(f"ORDER #{order_id} | {user} | {item} x{amount}")
        await self.ticket.create(guild, user, order_id)

        return order_id

    # =====================
    # ✅ COMPLETE ORDER (🔥 FIX ใหญ่)
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

                # 🔥 ไม่เช็ค READY แล้ว
                # 🔥 ไม่ใช้ stock แล้ว

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
