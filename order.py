import asyncio

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
    # 📢 ADMIN SEND
    # =====================
    async def send_admin(self, msg):
        try:
            ch_id = self.brain.get("CHANNELS.ORDER_NOTIFY")
            if not ch_id:
                return

            channel = self.bot.get_channel(int(ch_id)) or await self.bot.fetch_channel(int(ch_id))
            if channel:
                await channel.send(msg)

        except:
            pass

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

        await self.send_admin(
            f"📦 NEW ORDER #{order_id}\n"
            f"👤 {user}\n"
            f"📦 {item} x{amount}"
        )

        # 🔥 SAFE ALL SERVICES
        try:
            await self.notify.admin(user, item, order_id)
        except:
            pass

        try:
            await self.backup.log(f"ORDER #{order_id} | {user} | {item} x{amount}")
        except:
            pass

        try:
            await self.ticket.create(guild, user, order_id)
        except:
            pass

        return order_id

    # =====================
    # ✅ COMPLETE
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

            # =====================
            # 🔥 FARM FIX (ADDED)
            # =====================
            if not success:

                allow_farm = bool(self.brain.get("SETTINGS.ALLOW_FARM_IF_NO_STOCK", False))

                if allow_farm:
                    await self.farm_queue.put({
                        "item": item,
                        "amount": amount,
                        "order_id": order_id
                    })
                    await channel.send("⚠️ เข้าคิวฟาร์มแล้ว")
                    return False
                else:
                    await channel.send("❌ สต๊อกไม่พอ")
                    return False

            self.mem.update_order_status(order_id, "DONE")

            point = int(self.brain.get("SETTINGS.POINT_PER_ORDER") or 0)

            try:
                self.mem.add_points(user, point)
            except:
                pass

            await self.send_admin(
                f"✅ COMPLETE #{order_id}\n📦 {item} x{amount}"
            )

            await channel.send(
                f"✅ DONE\n📦 {item} x{amount}\n💰 +{point} points"
            )

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

            except:
                await asyncio.sleep(2)
