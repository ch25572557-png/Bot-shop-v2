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

        # 🧠 FARM QUEUE (NEW)
        self.farm_queue = []

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

        # =====================
        # 🔔 SAFE NOTIFY
        # =====================
        try:
            await self.notify.admin(user, item, order_id)
        except:
            pass

        # =====================
        # 💾 BACKUP
        # =====================
        try:
            await self.backup.log(
                f"ORDER #{order_id} | {user} | {item} x{amount}"
            )
        except:
            pass

        # =====================
        # 🎫 TICKET
        # =====================
        try:
            await self.ticket.create(guild, user, order_id)
        except:
            pass

        # =====================
        # 📊 DASHBOARD HOOK (NEW)
        # =====================
        try:
            if hasattr(self, "on_dashboard_update"):
                await self.on_dashboard_update()
        except:
            pass

        return order_id

    # =====================
    # 🔥 STOCK ALERT (SAFE)
    # =====================
    async def stock_alert(self, item, guild):

        try:
            low = int(self.brain.get("SETTINGS.LOW_STOCK") or 5)
            cd = int(self.brain.get("SETTINGS.STOCK_ALERT_COOLDOWN_SEC") or 60)
        except:
            low, cd = 5, 60

        qty = self.mem.get_stock(item)

        if qty > low:
            return

        key = f"{guild.id}:{item}"
        now = time.time()

        if key in self.last_alert:
            if now - self.last_alert[key] < cd:
                return

        self.last_alert[key] = now

        try:
            ch_id = self.brain.get("CHANNELS.STOCK_ALERT_CHANNEL")
            if not ch_id:
                return

            ch = guild.get_channel(int(ch_id))
            if ch:
                await ch.send(f"⚠️ STOCK ALERT\n📦 {item}\n📉 เหลือ {qty}")
        except:
            pass

    # =====================
    # 🧠 FARM QUEUE RUNNER (NEW REAL SYSTEM)
    # =====================
    async def farm_worker(self):

        while True:

            try:
                if not self.farm_queue:
                    await asyncio.sleep(2)
                    continue

                task = self.farm_queue.pop(0)

                item = task.get("item")
                amount = task.get("amount", 1)

                # 🔁 simulate farming delay
                await asyncio.sleep(3)

                # 📦 add stock back (farm success)
                cur = self.mem.conn.cursor()
                cur.execute(
                    "UPDATE stock SET qty = qty + ? WHERE name=?",
                    (amount, item)
                )
                self.mem.conn.commit()

            except:
                await asyncio.sleep(2)

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
            return False

        if status == "DONE":
            return False

        # =====================
        # 📦 STOCK LOCK
        # =====================
        async with self._lock:
            success = self.mem.minus_stock(item, amount)

        allow_farm = bool(self.brain.get("SETTINGS.ALLOW_FARM_IF_NO_STOCK", False))

        # =====================
        # 🟡 FARM MODE
        # =====================
        if not success:

            if allow_farm:

                await channel.send("⚠️ ไม่มีสต๊อก → เข้าคิวฟาร์ม")

                # 🧠 ADD TO FARM QUEUE (NEW)
                self.farm_queue.append({
                    "item": item,
                    "amount": amount,
                    "order_id": order_id
                })

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
            point = int(self.brain.get("SETTINGS.POINT_PER_ORDER") or 0)
        except:
            point = 0

        try:
            self.mem.add_points(user, point)
        except:
            pass

        # =====================
        # 🔥 STOCK ALERT
        # =====================
        try:
            await self.stock_alert(item, channel.guild)
        except:
            pass

        # =====================
        # 💾 BACKUP
        =====================
        try:
            await self.backup.log(
                f"COMPLETE #{order_id} | {user} | {item} x{amount}"
            )
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
