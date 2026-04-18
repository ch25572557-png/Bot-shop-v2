class OrderSystem:
    def __init__(self, mem, ticket, notify, backup, brain):
        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup
        self.brain = brain  # ใช้ดึง config (POINT_PER_ORDER)

    # =====================
    # 🛒 CREATE ORDER
    # =====================

    async def create(self, guild, user, item):

        # 🟢 create order
        order_id = self.mem.add_order(str(user), item, "WAIT")

        # 📢 notify admin
        try:
            await self.notify.admin(user, item)
        except:
            pass

        # 💾 backup log
        try:
            await self.backup.log(f"ORDER #{order_id} | {user} | {item}")
        except:
            pass

        # 🎫 create ticket (ส่ง order_id)
        try:
            await self.ticket.create(guild, user, order_id)
        except:
            pass

    # =====================
    # ✅ COMPLETE ORDER
    # =====================

    async def complete(self, channel):

        # 🔍 หา order_id จาก channel
        order_id = self.mem.get_order_by_channel(str(channel.id))

        if not order_id:
            return False

        # 🔍 ดึงข้อมูล order
        data = self.mem.get_order(order_id)

        if not data:
            return False

        user, item, status = data

        # ❗ กันกดซ้ำ
        if status == "DONE":
            return False

        # =====================
        # 🔄 UPDATE STATUS
        # =====================
        self.mem.update_order_status(order_id, "DONE")

        # =====================
        # 📦 MINUS STOCK
        # =====================
        success = self.mem.minus_stock(item)

        if not success:
            await channel.send("❌ สต็อกไม่พอ หรือสินค้าไม่มี")
            return False

        # =====================
        # 💰 ADD POINT
        # =====================
        try:
            point = int(self.brain.get("SETTINGS.POINT_PER_ORDER"))
        except:
            point = 0

        self.mem.add_points(user, point)

        # =====================
        # 💾 BACKUP LOG
        # =====================
        try:
            await self.backup.log(
                f"COMPLETE #{order_id} | {user} | {item}"
            )
        except:
            pass

        # =====================
        # 📢 แจ้งในห้อง
        # =====================
        try:
            await channel.send(
                f"✅ ออเดอร์เสร็จแล้ว\n"
                f"📦 {item}\n"
                f"💰 +{point} points\n"
                f"⏳ ห้องจะปิดใน 10 วินาที..."
            )
        except:
            pass

        # =====================
        # ⏱️ DELAY CLOSE
        # =====================
        import asyncio

        await asyncio.sleep(10)

        try:
            await channel.delete()
        except:
            pass

        return True
