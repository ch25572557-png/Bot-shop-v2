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
    # 🛒 CREATE ORDER (SAFE FLOW)
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

        # 🔔 ADMIN NOTIFY (must go admin order channel)
        try:
            await self.notify.admin(user, item, order_id)
        except Exception as e:
            print("[ORDER] notify error:", e)

        # 💾 BACKUP
        try:
            await self.backup.log(f"ORDER #{order_id} | {user} | {item} x{amount}")
        except Exception as e:
            print("[ORDER] backup error:", e)

        # 🎫 TICKET CREATE
        try:
            await self.ticket.create(guild, user, order_id)
        except Exception as e:
            print("[ORDER] ticket error:", e)

        return order_id

    # =====================
    # 🔥 STOCK ALERT (ANTI-SPAM + SAFE)
    # =====================
    async def stock_alert(self, item, guild):

        LOW = self.brain.get("SETTINGS.LOW_STOCK", 5)
        CD = self.brain.get("SETTINGS.COOLDOWN", 3)

        try:
            LOW = int(LOW)
            CD = int(CD)
        except:
            LOW = 5
            CD = 3

        qty = self.mem.get_stock(item)

        if qty > LOW:
            return

        key = f"{guild.id}:{item}"
        now = time.time()

        if key in self.last_alert:
            if now - self.last_alert[key] < CD * 60:
                return

        self.last_alert[key] = now

        try:
            admin_id = self.brain.get("CHANNELS.ADMIN")
            ch = guild.get_channel(int(admin_id))

            if ch:
                await ch.send(f"⚠️ STOCK ALERT\n📦 {item}\n📉 เหลือ {qty}")

        except Exception as e:
            print("[ORDER] stock alert error:", e)

    # =====================
    # ✅ COMPLETE ORDER (FINAL SAFE FLOW)
    # =====================
    async def complete(self, channel):

        order_id = self.mem.get_order_by_channel(str(channel.id))
        if not order_id:
            return False

        data = self.mem.get_order(order_id)
        if not data:
            return False

        # 🔒 SAFE UNPACK
        try:
            data = list(data) + [None] * 5
            user, item, amount, roblox_user, status = data[:5]
        except:
            return False

        if status == "DONE":
            return False

        # =====================
        # 📦 STOCK LOCK (FIX RACE CONDITION)
        # =====================
        async with self._lock:
            success = self.mem.minus_stock(item, amount)

        # 🟡 FARM MODE LOGIC (IMPORTANT FIX)
        if not success:
            allow_farm = self.brain.get("SETTINGS.ALLOW_FARM_IF_NO_STOCK", False)

            if allow_farm:
                try:
                    await channel.send("⚠️ ไม่มีสต๊อก → เข้าสู่โหมดฟาร์ม")
                except:
                    pass
            else:
                try:
                    await channel.send("❌ สต๊อกไม่พอ หรือสินค้าไม่มี")
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
        point = self.brain.get("SETTINGS.POINT_PER_ORDER", 0)

        try:
            point = int(point)
        except:
            point = 0

        try:
            self.mem.add_points(user, point)
        except Exception as e:
            print("[ORDER] points error:", e)

        # =====================
        # 🔥 STOCK ALERT CHECK
        # =====================
        try:
            await self.stock_alert(item, channel.guild)
        except Exception as e:
            print("[ORDER] alert error:", e)

        # =====================
        # 💾 BACKUP
        # =====================
        try:
            await self.backup.log(f"COMPLETE #{order_id} | {user} | {item} x{amount}")
        except Exception as e:
            print("[ORDER] backup error:", e)

        # =====================
        # 📢 MESSAGE
        # =====================
        try:
            msg = f"✅ ออเดอร์เสร็จแล้ว\n📦 {item} x{amount}\n💰 +{point} points"

            if roblox_user:
                msg += f"\n🎮 Roblox: {roblox_user}"

            msg += "\n⏳ ห้องจะปิดใน 10 วินาที..."

            await channel.send(msg)

        except Exception as e:
            print("[ORDER] message error:", e)

        # =====================
        # ⏱ CLOSE CHANNEL
        # =====================
        await asyncio.sleep(10)

        try:
            await channel.delete()
        except Exception as e:
            print("[ORDER] delete error:", e)

        return True
