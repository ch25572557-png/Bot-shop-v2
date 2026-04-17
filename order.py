class OrderSystem:
    def __init__(self, mem, ticket, notify, backup):
        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup

    async def create(self, guild, user, item):

        # 🟢 create order
        order_id = self.mem.add_order(str(user), item, "WAIT")

        # 📢 notify admin
        await self.notify.admin(user, item)

        # 💾 backup log
        await self.backup.log(f"ORDER #{order_id} | {user} | {item}")

        # 🎫 create ticket (ส่ง order_id)
        await self.ticket.create(guild, user, order_id)
