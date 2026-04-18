import asyncio
import time

class OrderSystem:
    def __init__(self, mem, ticket, notify, backup, brain):
        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup
        self.brain = brain

        self.last_alert = {}
        self._lock = asyncio.Lock()

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
            "WAIT"
        )

        if not order_id:
            return False

        try:
            await self.notify.admin(user, item, order_id)
        except Exception as e:
            print("[ORDER] notify error:", e)

        try:
            await self.backup.log(f"ORDER #{order_id} | {user} | {item} x{amount}")
        except Exception as e:
            print("[ORDER] backup error:", e)

        try:
            await self.ticket.create(guild, user, order_id)
        except Exception as e:
            print("[ORDER] ticket error:", e)

        return order_id

    # =====================
    # 🔥 STOCK ALERT
    # =====================
    async def stock_alert(self, item, guild):

        try:
            low = int(self.brain.get("SETTINGS.LOW_STOCK", 5))
            cd = int(self.brain.get("SETTINGS.COOLDOWN", 3))
        except:
            low, cd = 5, 3

        qty = self.mem.get_stock(item)

        if qty > low:
            return

        key = f"{guild.id}:{item}"
        now = time.time()

        if key in self.last_alert:
            if now - self.last_alert[key] < cd * 60:
                return

        self.last_alert[key] = now

        try:
            admin_id = self.brain.get("CHANNELS.ADMIN")
            if not admin_id:
                return

            ch = guild.get_channel(int(admin_id))
            if ch:
                await ch.send(f"⚠️ STOCK ALERT\n📦 {item}\n📉 เหลือ {qty}")

        except Exception as e:
            print("[ORDER] stock alert error:", e)

    # =====================
    # ✅ COMPLETE ORDER (FIXED FINAL)
    # =====================
    async def complete(self, channel):

        order_id = self.mem.get_order_by_channel(str(channel.id))
        if not order_id:
            return False

        data = self.mem.get_order(order_id)
        if not data:
            return False

        # 🔒 SAFE UNPACK (clean version)
        user = item = amount = roblox_user = status = None

        try:
            user, item, amount, roblox_user, status = data
        except:
            return False

        if status == "DONE":
            return False

        # =====================
        # 📦 STOCK LOCK
        # =====================
        async with self._lock:
            success = self.mem.minus_stock(item, amount)

        # =====================
        # 🟡 FARM MODE FIXED
        # =====================
        allow_farm = bool(self.brain.get("SETTINGS.ALLOW_FARM_IF_NO_STOCK", False))

        if not success:
            if allow_farm:
                await channel.send("⚠️ ไม่มีสต๊อก → โหมดฟาร์มทำงาน")
            else:
                await channel.send("❌ สต๊อกไม่พอ")
                return False

        # =====================
        # 🔄 UPDATE STATUS
        # =====================
        self.mem.update_order_status(order_id, "DONE")

        # =====================
        # 💰 POINTS
        # =====================
        try:
            point = int(self.brain.get("SETTINGS.POINT_PER_ORDER", 0))
        except:
            point = 0

        try:
            self.mem.add_points(user, point)
        except:
            pass

        # =====================
        # 🔥 ALERT
        # =====================
        try:
            await self.stock_alert(item, channel.guild)
        except:
            pass

        # =====================
        # 💾 BACKUP
        # =====================
        try:
            await self.backup.log(f"COMPLETE #{order_id} | {user} | {item} x{amount}")
        except:
            pass

        # =====================
        # 📢 MESSAGE
        # =====================
        try:
            msg = f"✅ DONE\n📦 {item} x{amount}\n💰 +{point} points"

            if roblox_user:
                msg += f"\n🎮 {roblox_user}"

            msg += "\n⏳ closing..."

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
