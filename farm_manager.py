import asyncio


class FarmManager:

    def __init__(self, mem, order_system):

        self.mem = mem
        self.order_system = order_system

        self.queue = asyncio.Queue()
        self.running = False

        self.processing = set()
        self.worker_count = 3  # 🔥 scale ได้

    # =====================
    # 🚀 START
    # =====================
    async def start(self):

        if self.running:
            return

        self.running = True

        for _ in range(self.worker_count):
            asyncio.create_task(self._worker())

        print(f"🌾 FARM MANAGER STARTED ({self.worker_count} workers)")

    # =====================
    # ➕ ADD JOB
    # =====================
    async def add_job(self, order_id, item, amount):

        # 🔥 กันซ้ำทั้ง queue + processing
        if order_id in self.processing:
            return

        await self.queue.put({
            "order_id": order_id,
            "item": item,
            "amount": amount
        })

    # =====================
    # 🔁 WORKER
    # =====================
    async def _worker(self):

        while self.running:

            try:
                try:
                    job = await asyncio.wait_for(self.queue.get(), timeout=3)

                    order_id = job["order_id"]
                    item = job["item"]
                    amount = job["amount"]

                except asyncio.TimeoutError:
                    # 🔥 recovery จาก DB
                    rows = await self.mem.get_pending_farm(5)

                    if not rows:
                        await asyncio.sleep(2)
                        continue

                    order_id, item, amount = rows[0]

                # 🔥 กันซ้ำ
                if order_id in self.processing:
                    continue

                self.processing.add(order_id)

                try:
                    # 🔥 เช็คสถานะก่อน
                    data = await self.mem.get_order(order_id)
                    if not data:
                        continue

                    _, _, _, _, status = data

                    if status != "FARMING":
                        continue

                    # =====================
                    # 🌾 FARM
                    # =====================
                    await asyncio.sleep(2)

                    await self.mem.add_stock(item, amount)

                    # 🔥 ใช้ READY (สำคัญ)
                    await self.mem.update_order_status(order_id, "READY")

                    await self.order_system.send_ticket(
                        order_id,
                        "🌾 ฟาร์มเสร็จแล้ว พร้อมส่ง"
                    )

                finally:
                    self.processing.discard(order_id)

            except Exception as e:
                print("[FARM ERROR]", e)
                await asyncio.sleep(2)
