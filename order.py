class OrderSystem:
    def __init__(self, mem, ticket, notify, backup):
        self.mem = mem
        self.ticket = ticket
        self.notify = notify
        self.backup = backup

    async def create(self, guild, user, item):

        self.mem.cur.execute(
            "INSERT INTO orders (user, item, status) VALUES (?,?,?)",
            (str(user), item, "WAIT")
        )
        self.mem.conn.commit()

        await self.notify.admin(user, item)
        await self.backup.log(f"ORDER | {user} | {item}")
        await self.ticket.create(guild, user, "ORDER")
