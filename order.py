import asyncio
import time

class OrderSystem:
    def __init__(self, mem, ticket, notify, backup, brain):
        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup
        self.brain = brain

        # 🟡 cooldown storage (stock alert)
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

        if not order_id:
            return False

        # 📢 notify admin
        try:
            await self.notify.admin(user, item, order_id)
        except Exception as e:
            print("[ORDER] notify error:", e)

        # 💾 backup
        try:
            await self.backup.log(
                f"ORDER #{order_id} | {user} | {item} x{amount}"
            )
        except Exception as e:
            print("[ORDER] backup error:", e)

        # 🎫 ticket
        try:
            await self.ticket.create(guild, user, order_id)
        except Exception as e:
            print("[ORDER] ticket error:", e)

        return order_id

    # =====================
    # 🔥 STOCK ALERT SYSTEM (C CORE)
    # =====================
    async def stock_alert(self, item, guild):

        try:
            LOW_STOCK = int(self.brain.get("SETTINGS.LOW_STOCK") or 5)
        except:
            LOW_STOCK = 5

        try:
            COOLDOWN = int(self.brain.get("SETTINGS.COOLDOWN") or 3)
        except:
            COOLDOWN = 3

        qty = self.mem.get_stock(item)

        if qty > LOW_STOCK:
            return

        now = time.time()

        # ⏳ anti spam per item
        if item in self.last_alert:
            if now - self.last_alert[item] < COOLDOWN * 60:
                return

        self.last_alert[item] = now

        try:
            admin_id = self.brain.get("CHANNELS.ADMIN")
            admin_ch = guild.get_channel(int(admin_id))

            if admin_ch:
                await admin_ch.send(
                    f"⚠️ STOCK ALERT\n📦 {item}\n📉 เหลือ {qty}"
                )

        except Exception as e:
            print("[ORDER] stock alert error:", e)

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

        # 🔒 lock prevent double complete
        if status == "DONE":
            return False

        # =====================
        # 📦 STOCK (must pass first)
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
            await self.backup.log(
                f"COMPLETE #{order_id} | {user} | {item} x{amount}"
            )
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
        # ⏱ CLOSE
        # =====================
        await asyncio.sleep(10)

        try:
            await channel.delete()
        except Exception as e:
            print("[ORDER] delete channel error:", e)

        return True
