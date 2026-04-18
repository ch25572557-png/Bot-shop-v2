class OrderSystem:
    def __init__(self, mem, ticket, notify, backup, brain):
        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup
        self.brain = brain

    # =====================
    # 🛒 CREATE ORDER
    # =====================
    async def create(self, guild, user, item, amount=1, roblox_user=None):

        # 🔒 กัน input พัง
        try:
            amount = int(amount)
            if amount <= 0:
                amount = 1
        except:
            amount = 1

        # 🟢 create order
        order_id = self.mem.add_order(
            str(user),
            item,
            amount,
            roblox_user,
            "WAIT"
        )

        # 📢 notify admin
        try:
            await self.notify.admin(user, item, order_id)
        except:
            pass

        # 💾 backup log
        try:
            await self.backup.log(
                f"ORDER #{order_id} | {user} | {item} x{amount} | {roblox_user}"
            )
        except:
            pass

        # 🎫 create ticket
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

        # 🧠 รองรับโครงใหม่ (และ fallback เผื่อ)
        try:
            user, item, amount, roblox_user, status = data
        except:
            user, item, status = data
            amount = 1
            roblox_user = None

        # ❗ กันกดซ้ำ
        if status == "DONE":
            return False

        # =====================
        # 📦 MINUS STOCK (ทำก่อน)
        # =====================
        success = self.mem.minus_stock(item, amount)

        if not success:
            try:
                await channel.send("❌ สต็อกไม่พอ หรือสินค้าไม่มี")
            except:
                pass
            return False

        # =====================
        # 🔄 UPDATE STATUS
        # =====================
        self.mem.update_order_status(order_id, "DONE")

        # =====================
        # 💰 ADD POINT
        # =====================
        try:
            point = int(self.brain.get("SETTINGS.POINT_PER_ORDER"))
        except:
            point = 0

        try:
            self.mem.add_points(user, point)
        except:
            pass

        # =====================
        # 💾 BACKUP LOG
        # =====================
        try:
            await self.backup.log(
                f"COMPLETE #{order_id} | {user} | {item} x{amount} | {roblox_user}"
            )
        except:
            pass

        # =====================
        # 📢 แจ้งในห้อง
        # =====================
        try:
            msg = (
                f"✅ ออเดอร์เสร็จแล้ว\n"
                f"📦 {item} x{amount}\n"
            )

            if roblox_user:
                msg += f"🎮 Roblox: {roblox_user}\n"

            msg += (
                f"💰 +{point} points\n"
                f"⏳ ห้องจะปิดใน 10 วินาที..."
            )

            await channel.send(msg)
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
