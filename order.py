import asyncio
import time

class OrderSystem:
    def __init__(self, mem, ticket, notify, backup, brain):
        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup
        self.brain = brain

        # 🟡 cooldown storage
        self.last_alert = {}

    # =====================
    # 🛒 CREATE ORDER
    # =====================
    async def create(self, guild, user, item, amount=1, roblox_user=None):

        try:
            amount = int(amount)
            if amount <= 0:
                amount = 1
        except:
            amount = 1

        order_id = self.mem.add_order(
            str(user),
            item,
            amount,
            roblox_user,
            "WAIT"
        )

        try:
            await self.notify.admin(user, item, order_id)
        except:
            pass

        try:
            await self.backup.log(
                f"ORDER #{order_id} | {user} | {item} x{amount} | {roblox_user}"
            )
        except:
            pass

        try:
            await self.ticket.create(guild, user, order_id)
        except:
            pass

    # =====================
    # 🔥 STOCK ALERT SYSTEM
    # =====================
    async def stock_alert(self, item, channel):

        LOW_STOCK = int(self.brain.get("SETTINGS.LOW_STOCK") or 5)
        COOLDOWN = int(self.brain.get("SETTINGS.COOLDOWN") or 3)

        qty = self.mem.get_stock(item)

        if qty > LOW_STOCK:
            return

        now = time.time()

        # ⏳ cooldown กัน spam
        if item in self.last_alert:
            if now - self.last_alert[item] < COOLDOWN * 60:
                return

        self.last_alert[item] = now

        try:
            admin_ch = channel.guild.get_channel(
                int(self.brain.get("CHANNELS.ADMIN"))
            )

            if admin_ch:
                await admin_ch.send(
                    f"⚠️ STOCK ALERT\n📦 {item}\n📉 เหลือ {qty}"
                )
        except:
            pass

    # =====================
    # ✅ COMPLETE ORDER
    # =====================
    async def complete(self, channel):

        order_id = self.mem.get_order_by_channel(str(channel.id))
        if not order_id:
            return False

        data = self.mem.get_order(order_id)
        if not data:
            return False

        try:
            user, item, amount, roblox_user, status = data
        except:
            user, item, status = data
            amount = 1
            roblox_user = None

        if status == "DONE":
            return False

        # =====================
        # 📦 MINUS STOCK (ก่อน DONE)
        # =====================
        success = self.mem.minus_stock(item, amount)

        if not success:
            try:
                await channel.send("❌ สต็อกไม่พอ หรือสินค้าไม่มี")
            except:
                pass
            return False

        # =====================
        # 🔄 UPDATE STATUS
        # =====================
        self.mem.update_order_status(order_id, "DONE")

        # =====================
        # 💰 POINTS
        # =====================
        try:
            point = int(self.brain.get("SETTINGS.POINT_PER_ORDER"))
        except:
            point = 0

        try:
            self.mem.add_points(user, point)
        except:
            pass

        # =====================
        # 🔥 STOCK ALERT CHECK
        # =====================
        await self.stock_alert(item, channel)

        # =====================
        # 💾 BACKUP
        # =====================
        try:
            await self.backup.log(
                f"COMPLETE #{order_id} | {user} | {item} x{amount} | {roblox_user}"
            )
        except:
            pass

        # =====================
        # 📢 MESSAGE
        # =====================
        try:
            msg = (
                f"✅ ออเดอร์เสร็จแล้ว\n"
                f"📦 {item} x{amount}\n"
                f"💰 +{point} points\n"
            )

            if roblox_user:
                msg += f"🎮 Roblox: {roblox_user}\n"

            msg += "⏳ ห้องจะปิดใน 10 วินาที..."

            await channel.send(msg)
        except:
            pass

        # =====================
        # ⏱ CLOSE
        # =====================
        await asyncio.sleep(10)

        try:
            await channel.delete()
        except:
            pass

        return True
