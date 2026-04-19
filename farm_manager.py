import asyncio


class FarmManager:

    def __init__(self, mem, brain, order_system):

        self.mem = mem
        self.brain = brain
        self.order_system = order_system

        self.queue = asyncio.Queue()
        self.running = False

    # =====================
    # 🚀 START
    # =====================
    async def start(self):

        if self.running:
            return

        self.running = True
        asyncio.create_task(self._worker())

        print("🌾 FARM MANAGER V3 STARTED")

    # =====================
    # ➕ ADD JOB
    # =====================
    async def add_job(self, order_id, item, amount):

        await self.queue.put({
            "order_id": order_id,
            "item": item,
            "amount": amount
        })

    # =====================
    # 🔁 MAIN WORKER
    # =====================
    async def _worker(self):

        while self.running:

            try:
                job = await self.queue.get()

                order_id = job["order_id"]
                item = job["item"]
                amount = job["amount"]

                # =====================
                # 🌾 FARM DELAY (simulate)
                # =====================
                await asyncio.sleep(2)

                # =====================
                # 📦 ADD STOCK
                # =====================
                await self.mem.add_stock(item, amount)

                # =====================
                # 📊 UPDATE STATUS
                # =====================
                await self.mem.update_order_status(order_id, "FARMED")

                # =====================
                # 📢 NOTIFY BACK TO ORDER SYSTEM
                # =====================
                await self.order_system.send_ticket(
                    order_id,
                    "🌾 ฟาร์มเสร็จแล้ว พร้อมส่ง"
                )

            except Exception as e:
                print("[FARM MANAGER ERROR]", e)
                await asyncio.sleep(2)
