class OrderSystem:
    def __init__(self, mem, ticket, notify):
        self.mem = mem
        self.ticket = ticket
        self.notify = notify

    async def create(self, guild, user, item):

        self.mem.cur.execute(
            "INSERT INTO orders VALUES(?,?,?)",
            (str(user), item, "WAIT")
        )
        self.mem.conn.commit()

        await self.notify.admin(user, item)
        await self.ticket.create(guild, user, "ORDER")
