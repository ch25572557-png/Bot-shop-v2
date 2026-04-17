class StatusSystem:
    def __init__(self, mem):
        self.mem = mem

    def set(self, status):
        self.mem.cur.execute(
            "UPDATE orders SET status=?",
            (status,)
        )
        self.mem.conn.commit()

    def get(self, user):
        self.mem.cur.execute(
            "SELECT status FROM orders WHERE user=?",
            (str(user),)
        )
        return self.mem.cur.fetchone()
