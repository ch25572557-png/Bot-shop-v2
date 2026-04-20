import asyncio


class FarmManager:

    def __init__(self, mem, order_system):

        self.mem = mem
        self.order_system = order_system

        self.queue = asyncio.Queue()
        self.running = False

        self.processing = set()
        self.queued = set()

        self.worker_count = 3

        # 🔥 lock กัน recovery ชนกัน
        self._recovery_lock = asyncio.Lock()

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
    # 🛑 STOP (NEW)
    # =====================
    async def stop(self):
        self.running = False

    # =====================
    # ➕ ADD JOB
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

                    # 🔥 lock recovery กัน worker แย่งกัน
                    async with self._recovery_lock:

                        rows = await self.mem.get_pending_farm(5)

                        for oid, item, amount in rows:
                            if oid not in self.processing and oid not in self.queued:
                                await self.add_job(oid, item, amount)

                    await asyncio.sleep(1)
                    continue

                order_id = job["order_id"]
                item = job["item"]
                amount = job["amount"]
                retry = job.get("retry", 0)

                # =====================
                # 🔒 LOCK
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
                    print(f"[FARM SKIP] #{order_id} not found")
                    continue

                _, _, _, _, status = data

                if status != "FARMING":
                    print(f"[FARM SKIP] #{order_id} status={status}")
                    continue

                # =====================
                # 🌾 FARM
                # =====================
                await asyncio.sleep(2)

                # 🔥 DOUBLE CHECK ก่อนเพิ่ม stock
                stock = await self.mem.get_stock(item)

                if stock >= amount:
                    print(f"[FARM SKIP] #{order_id} stock already enough")
                else:
                    await self.mem.add_stock(item, amount)

                await self.mem.update_order_status(order_id, "READY")

                await self.order_system.send_ticket(
                    order_id,
                    "🌾 ฟาร์มเสร็จแล้ว พร้อมส่ง"
                )

                print(f"[FARM OK] #{order_id} by worker {wid}")

            except Exception as e:

                print(f"[FARM ERROR] worker={wid} job={job} err={e}")

                # =====================
                # 🔁 RETRY
                # =====================
                if job and job.get("retry", 0) < 3:

                    job["retry"] += 1

                    # 🔥 reset queued ก่อน retry
                    self.queued.discard(job["order_id"])

                    await asyncio.sleep(1)
                    await self.queue.put(job)

            finally:

                if job:
                    self.processing.discard(job["order_id"])
                    self.queue.task_done()
