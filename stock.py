class StockSystem:
    def __init__(self, mem):
        self.mem = mem

    # =====================
    # 📦 MINUS STOCK (ATOMIC SAFE)
    # =====================
    def minus(self, item, amount=1):

        try:
            amount = int(amount)
            if amount <= 0:
                amount = 1
        except:
            amount = 1

        # 🔒 atomic update (กัน stock ติดลบ)
        self.mem.cur.execute(
            "UPDATE stock SET qty = qty - ? WHERE name=? AND qty >= ?",
            (amount, item, amount)
        )

        self.mem.conn.commit()

        return self.mem.cur.rowcount > 0

    # =====================
    # ➕ ADD / UPDATE STOCK
    # =====================
    def add(self, name, qty, price):

        try:
            qty = int(qty)
            price = float(price)
        except:
            return False

        # 🔍 check exists
        self.mem.cur.execute(
            "SELECT qty FROM stock WHERE name=?",
            (name,)
        )
        result = self.mem.cur.fetchone()

        if result:
            # ➕ update stock
            self.mem.cur.execute(
                "UPDATE stock SET qty = qty + ?, price=? WHERE name=?",
                (qty, price, name)
            )
        else:
            # 🆕 insert new
            self.mem.cur.execute(
                "INSERT INTO stock(name, qty, price) VALUES(?,?,?)",
                (name, qty, price)
            )

        self.mem.conn.commit()
        return True

    # =====================
    # 📊 GET STOCK
    # =====================
    def get(self, item):
        self.mem.cur.execute(
            "SELECT qty FROM stock WHERE name=?",
            (item,)
        )
        result = self.mem.cur.fetchone()
        return result[0] if result else 0
