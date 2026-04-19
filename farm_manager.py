import asyncio


class FarmManager:

    def __init__(self, mem, brain, order_system):

        self.mem = mem
        self.brain = brain
        self.order_system = order_system

        self.queue = asyncio.Queue()
        self.running = False

        # 🔥 protection
        self.processing = set()

    # =====================
    # 🚀 START
    # =====================
    async def start(self):

        if self.running:
            return

        self.running = True
        asyncio.create_task(self._worker())

        print("🌾 FARM MANAGER V3 STABLE STARTED")

    # =====================
    # ➕ ADD JOB (SAFE)
    # =====================
    async def add_job(self, order_id, item, amount):

        # 🔥 prevent duplicate farm
        if order_id in self.processing:
            return

        await self.queue.put({
            "order_id": order_id,
            "item": item,
            "amount": amount
        })

    # =====================
    # 🔁 WORKER CORE
    # =====================
    async def _worker(self):

        while self.running:

            try:
                job = await self.queue.get()

                order_id = job["order_id"]
                item = job["item"]
                amount = job["amount"]

                # 🔥 mark processing
                self.processing.add(order_id)

                # =====================
                # 🌾 FARM SIMULATION
                # =====================
                await asyncio.sleep(2)

                # =====================
                # 📦 ADD STOCK
                # =====================
                await self.mem.add_stock(item, amount)

                # =====================
                # 📊 STATUS UPDATE
                # =====================
                await self.mem.update_order_status(order_id, "FARMED")

                # =====================
                # 📢 BACK TO ORDER SYSTEM
                # =====================
                await self.order_system.send_ticket(
                    order_id,
                    "🌾 ฟาร์มเสร็จแล้ว (READY TO SEND)"
                )

            except Exception as e:
                print("[FARM MANAGER ERROR]", e)
                await asyncio.sleep(2)

            finally:
                # 🔥 always cleanup
                if "order_id" in locals():
                    self.processing.discard(order_id)
