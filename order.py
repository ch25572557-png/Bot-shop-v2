import asyncio
import time

class OrderSystem:
    def __init__(self, mem, ticket, notify, backup, brain, bot):

        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup
        self.brain = brain
        self.bot = bot

        self.last_alert = {}
        self._lock = asyncio.Lock()
        self.farm_queue = asyncio.Queue()

        self._started = False

    # =====================
    # 🚀 START
    # =====================
    async def start(self):
        if self._started:
            return
        self._started = True
        asyncio.create_task(self.farm_worker())

    # =====================
    # 📢 ADMIN SEND (FIX 100%)
    # =====================
    async def send_admin(self, msg):
        try:
            ch_id = (
                self.brain.get("ORDER_NOTIFY")
                or self.brain.get("CHANNELS.ORDER_NOTIFY")
            )

            if not ch_id:
                return

            channel = None

            try:
                channel = self.bot.get_channel(int(ch_id))
                if channel is None:
                    channel = await self.bot.fetch_channel(int(ch_id))
            except:
                return

            if channel:
                await channel.send(msg)

        except Exception as e:
            print("[ADMIN SEND ERROR]", e)

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

        # 🔥 SEND TO ADMIN (FIXED)
        await self.send_admin(
            f"📦 NEW ORDER #{order_id}\n"
            f"👤 {user}\n"
            f"📦 {item} x{amount}"
        )

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
    # 🧠 FARM WORKER
    # =====================
    async def farm_worker(self):
        while True:
            try:
                task = await self.farm_queue.get()

                item = task["item"]
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
