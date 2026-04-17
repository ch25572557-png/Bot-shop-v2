class StatusSystem:
    def __init__(self, mem):
        self.mem = mem

    def set(self, order_id, status):
        self.mem.update_order_status(order_id, status)

    def get(self, order_id):
        self.mem.cur.execute(
            "SELECT status FROM orders WHERE id=?",
            (order_id,)
        )
        return self.mem.cur.fetchone()
