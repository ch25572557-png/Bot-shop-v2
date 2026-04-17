class OrderSystem:
    def __init__(self, mem, ticket, notify, backup):
        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup

    async def create(self, guild, user, item):

        # 🟢 ใช้ Memory แทน SQL ตรง
        order_id = self.mem.add_order(str(user), item, "WAIT")

        # 📢 แจ้งแอดมิน
        await self.notify.admin(user, item)

        # 💾 log backup
        await self.backup.log(f"ORDER #{order_id} | {user} | {item}")

        # 🎫 สร้าง ticket (ส่ง order_id ไปด้วยจะดีมาก)
        await self.ticket.create(guild, user, f"ORDER #{order_id}")
