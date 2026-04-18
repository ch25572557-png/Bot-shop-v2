import asyncio
import time

class OrderSystem:
    def __init__(self, mem, ticket, notify, backup, brain, bot):

        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup
        self.brain = brain
        self.bot = bot  # 🔥 FIX: ใช้ส่งไปแอดมิน

        self.last_alert = {}
        self._lock = asyncio.Lock()
        self.farm_queue = asyncio.Queue()

        self._started = False

    # =====================
    # 🚀 START (เรียกจาก bot.py เท่านั้น)
    # =====================
    async def start(self):
        if self._started:
            return
        self._started = True

        asyncio.create_task(self.farm_worker())
        print("🧠 FARM WORKER STARTED")

    # =====================
    # 🛒 CREATE ORDER (FIX: ส่งเข้า ADMIN CHANNEL)
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
        # 📢 SEND TO ADMIN CHANNEL (FIX หลัก)
        # =====================
        try:
            ch_id = self.brain.get("CHANNELS.ORDER_NOTIFY")

            if ch_id:
                ch = self.bot.get_channel(int(ch_id)) or await self.bot.fetch_channel(int(ch_id))

                if ch:
                    await ch.send(
                        f"📦 NEW ORDER #{order_id}\n"
                        f"👤 {user}\n"
                        f"📦 {item} x{amount}"
                    )
        except Exception as e:
            print("[ADMIN SEND ERROR]", e)

        # =====================
        # NOTIFY ADMIN DM
        # =====================
        try:
            await self.notify.admin(user, item, order_id)
        except:
            pass

        try:
            await self.backup.log(
                f"ORDER #{order_id} | {user} | {item} x{amount}"
            )
        except:
            pass

        try:
            await self.ticket.create(guild, user, order_id)
        except:
            pass

        return order_id

    # =====================
    # 🧠 FARM WORKER (UNCHANGED BUT SAFE)
    # =====================
    async def farm_worker(self):

        while True:
            try:
                task = await self.farm_queue.get()

                item = task.get("item")
                amount = task.get("amount", 1)

                await asyncio.sleep(3)

                cur = self.mem.conn.cursor()
                cur.execute(
                    "UPDATE stock SET qty = qty + ? WHERE name=?",
                    (amount, item)
                )
                self.mem.conn.commit()

            except Exception as e:
                print("[FARM ERROR]", e)
                await asyncio.sleep(2)

    # =====================
    # COMPLETE (UNCHANGED LOGIC)
    # =====================
    async def complete(self, channel):

        order_id = self.mem.get_order_by_channel(str(channel.id))
        if not order_id:
            return False

        data = self.mem.get_order(order_id)
        if not data:
            return False

        user, item, amount, roblox_user, status = data

        if status == "DONE":
            return False

        async with self._lock:
            success = self.mem.minus_stock(item, amount)

        allow_farm = bool(self.brain.get("SETTINGS.ALLOW_FARM_IF_NO_STOCK", False))

        if not success:

            if allow_farm:
                await channel.send("⚠️ ไม่มีสต๊อก → เข้าคิวฟาร์ม")

                await self.farm_queue.put({
                    "item": item,
                    "amount": amount,
                    "order_id": order_id
                })

            else:
                await channel.send("❌ สต๊อกไม่พอ")
                return False

        self.mem.update_order_status(order_id, "DONE")

        point = int(self.brain.get("SETTINGS.POINT_PER_ORDER") or 0)

        try:
            self.mem.add_points(user, point)
        except:
            pass

        try:
            await self.stock_alert(item, channel.guild)
        except:
            pass

        try:
            await self.backup.log(
                f"COMPLETE #{order_id} | {user} | {item} x{amount}"
            )
        except:
            pass

        try:
            msg = f"✅ DONE\n📦 {item} x{amount}\n💰 +{point} points"

            if roblox_user:
                msg += f"\n🎮 {roblox_user}"

            await channel.send(msg)
        except:
            pass

        await asyncio.sleep(10)

        try:
            await channel.delete()
        except:
            pass

        return True
