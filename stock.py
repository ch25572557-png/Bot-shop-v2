class StockSystem:
    def __init__(self, mem):
        self.mem = mem

    # =====================
    # 📦 MINUS STOCK (ปลอดภัย)
    # =====================
    def minus(self, item, amount=1):
        self.mem.cur.execute(
            "SELECT qty FROM stock WHERE name=?",
            (item,)
        )
        result = self.mem.cur.fetchone()

        if not result:
            return False  # ไม่มีสินค้า

        qty = result[0]

        if qty < amount:
            return False  # ของไม่พอ

        self.mem.cur.execute(
            "UPDATE stock SET qty = qty - ? WHERE name=?",
            (amount, item)
        )
        self.mem.conn.commit()
        return True

    # =====================
    # ➕ ADD / UPDATE STOCK
    # =====================
    def add(self, name, qty, price):

        # เช็คว่ามีอยู่แล้วไหม
        self.mem.cur.execute(
            "SELECT qty FROM stock WHERE name=?",
            (name,)
        )
        result = self.mem.cur.fetchone()

        if result:
            # ถ้ามี → เพิ่ม qty
            self.mem.cur.execute(
                "UPDATE stock SET qty = qty + ?, price=? WHERE name=?",
                (qty, price, name)
            )
        else:
            # ถ้าไม่มี → สร้างใหม่
            self.mem.cur.execute(
                "INSERT INTO stock(name, qty, price) VALUES(?,?,?)",
                (name, qty, price)
            )

        self.mem.conn.commit()
        return True
