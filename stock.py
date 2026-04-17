class StockSystem:
    def __init__(self, mem):
        self.mem = mem

    def minus(self, item):
        self.mem.cur.execute(
            "UPDATE stock SET qty=qty-1 WHERE name=?",
            (item,)
        )
        self.mem.conn.commit()

    def add(self, name, qty, price):
        self.mem.cur.execute(
            "INSERT INTO stock VALUES(?,?,?)",
            (name, qty, price)
        )
        self.mem.conn.commit()
