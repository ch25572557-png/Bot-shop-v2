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

        # 🔥 ไม่ผูก stock → FARMING เลย
        await self.mem.update_order_status(order_id, "FARMING")

        if self.farm_manager:
            await self.farm_manager.add_job(order_id, item, amount)

        await self.notify.admin(user, item, order_id)
        await self.backup.log(f"ORDER #{order_id} | {user} | {item} x{amount}")
        await self.ticket.create(guild, user, order_id)

        return order_id

    # =====================
    # ✅ COMPLETE ORDER (FINAL FIX)
    # =====================
    async def complete(self, channel, interaction=None):

        order_id = await self.mem.get_order_by_channel(str(channel.id))
        if not order_id:
            await channel.send("❌ ไม่พบออเดอร์")
            return False

        if order_id in self.processing:
            return False

        self.processing.add(order_id)

        try:
            async with self._lock:

                data = await self.mem.get_order(order_id)
                if not data:
                    await channel.send("❌ ไม่พบข้อมูลออเดอร์")
                    return False

                user, item, amount, roblox_user, status = data
                item = item.lower().strip()

                # 🔥 กันกดซ้ำ
                if status == "DONE":
                    await channel.send("⚠️ ออเดอร์นี้เสร็จแล้ว")
                    return False

                # =====================
                # 📦 TRY CUT STOCK (ไม่บังคับ)
                # =====================
                stock_msg = ""

                try:
                    ok = await self.mem.minus_stock(item, amount)

                    if ok:
                        stock_msg = f"📦 หักสต๊อกแล้ว ({item} -{amount})"
                    else:
                        stock_msg = "⚠️ สต๊อกไม่พอ → ข้าม"

                except Exception as e:
                    print("[STOCK SKIP]", e)
                    stock_msg = "⚠️ ข้ามการหักสต๊อก"

                # =====================
                # ✅ COMPLETE
                # =====================
                await self.mem.update_order_status(order_id, "DONE")

                point = int(self.brain.setting("POINT_PER_ORDER", 0))
                await self.mem.add_points(user, point)

                await self.notify.complete(user, item, order_id)
                await self.backup.complete(order_id, user, item)

                await self.send_ticket(order_id, "✅ ส่งของแล้ว")

                await channel.send(
                    embed=discord.Embed(
                        title="✅ DONE",
                        description=f"{item} x{amount}\n+{point} points\n\n{stock_msg}",
                        color=0x00ff00
                    )
                )

                # 🔥 รอให้ message ส่งก่อนค่อยลบ
                await asyncio.sleep(3)

                try:
                    fresh = self.bot.get_channel(channel.id) or await self.bot.fetch_channel(channel.id)
                    if fresh:
                        await fresh.delete(reason=f"Order #{order_id} completed")
                except Exception as e:
                    print("[DELETE ERROR]", e)

                return True

        finally:
            self.processing.discard(order_id)
