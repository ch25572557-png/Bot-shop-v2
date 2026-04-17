# 🟢 เพิ่มออเดอร์ (คืน id)
def add_order(self, user, item, status="WAIT"):
    self.cur.execute(
        "INSERT INTO orders(user,item,status) VALUES(?,?,?)",
        (str(user), item, status)
    )
    self.conn.commit()
    return self.cur.lastrowid


# 🟢 ดึงออเดอร์
def get_order(self, order_id):
    self.cur.execute(
        "SELECT * FROM orders WHERE id=?",
        (order_id,)
    )
    return self.cur.fetchone()


# 🟢 อัปเดต status
def update_order_status(self, order_id, status):
    self.cur.execute(
        "UPDATE orders SET status=? WHERE id=?",
        (status, order_id)
    )
    self.conn.commit()


# 🟢 ลด stock แบบกันติดลบ
def minus_stock(self, name):
    self.cur.execute(
        "UPDATE stock SET qty = MAX(qty - 1, 0) WHERE name=?",
        (name,)
    )
    self.conn.commit()
