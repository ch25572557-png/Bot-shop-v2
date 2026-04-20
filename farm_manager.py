import asyncio


class FarmManager:

    def __init__(self, mem, order_system):

        self.mem = mem
        self.order_system = order_system

        self.queue = asyncio.Queue()
        self.running = False

        self.processing = set()
        self.queued = set()  # 🔥 กันซ้ำระดับ queue
        self.worker_count = 3

    # =====================
    # 🚀 START
    # =====================
    async def start(self):

        if self.running:
            return

        self.running = True

        for i in range(self.worker_count):
            asyncio.create_task(self._worker(i))

        print(f"🌾 FARM MANAGER STARTED ({self.worker_count} workers)")

    # =====================
    # ➕ ADD JOB (SAFE)
    # =====================
    async def add_job(self, order_id, item, amount):

        if order_id in self.processing or order_id in self.queued:
            return

        self.queued.add(order_id)

        await self.queue.put({
            "order_id": order_id,
            "item": item,
            "amount": amount,
            "retry": 0
        })

    # =====================
    # 🔁 WORKER
    # =====================
    async def _worker(self, wid):

        while self.running:

            job = None

            try:
                # =====================
                # 📥 GET JOB
                # =====================
                try:
                    job = await asyncio.wait_for(self.queue.get(), timeout=3)

                except asyncio.TimeoutError:
                    # 🔥 recovery multi-job
                    rows = await self.mem.get_pending_farm(5)

                    for r in rows:
                        oid, item, amount = r

                        if oid not in self.processing and oid not in self.queued:
                            await self.add_job(oid, item, amount)

                    await asyncio.sleep(1)
                    continue

                order_id = job["order_id"]
                item = job["item"]
                amount = job["amount"]
                retry = job.get("retry", 0)

                # =====================
                # 🔒 LOCK ORDER
                # =====================
                if order_id in self.processing:
                    continue

                self.processing.add(order_id)
                self.queued.discard(order_id)

                # =====================
                # 🔍 VALIDATE
                # =====================
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

                await self.mem.update_order_status(order_id, "READY")

                await self.order_system.send_ticket(
                    order_id,
                    "🌾 ฟาร์มเสร็จแล้ว พร้อมส่ง"
                )

                print(f"[FARM OK] #{order_id} by worker {wid}")

            except Exception as e:
                print("[FARM ERROR]", e)

                # 🔥 retry (max 3)
                if job and job.get("retry", 0) < 3:
                    job["retry"] += 1
                    await self.queue.put(job)

            finally:
                if job:
                    self.processing.discard(job["order_id"])
                    self.queue.task_done()
