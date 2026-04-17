class StatusSystem:
    def __init__(self, mem):
        self.mem = mem

    def set(self, user, status):
        self.mem.cur.execute(
            "UPDATE orders SET status=? WHERE user=?",
            (status, str(user))
        )
        self.mem.conn.commit()

    def get(self, user):
        self.mem.cur.execute(
            "SELECT status FROM orders WHERE user=?",
            (str(user),)
        )
        data = self.mem.cur.fetchone()
        return data[0] if data else None
