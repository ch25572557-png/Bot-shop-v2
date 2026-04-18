import threading

class StockSystem:
    def __init__(self, mem):
        self.mem = mem
        self.lock = threading.Lock()

    # =====================
    # 📦 MINUS STOCK (ATOMIC + SAFE FINAL)
    # =====================
    def minus(self, item, amount=1):

        try:
            amount = int(amount)
            if amount <= 0:
                amount = 1
        except:
            amount = 1

        try:
            with self.lock:
                cur = self.mem.conn.cursor()

                cur.execute(
                    """
                    UPDATE stock
                    SET qty = qty - ?
                    WHERE name = ? AND qty >= ?
                    """,
                    (amount, item, amount)
                )

                self.mem.conn.commit()

                return cur.rowcount > 0

        except Exception as e:
            print("[STOCK] minus error:", e)
            return False

    # =====================
    # ➕ ADD STOCK (SAFE UPSERT STYLE)
    # =====================
    def add(self, name, qty, price):

        try:
            qty = int(qty)
            price = float(price)
        except:
            return False

        try:
            with self.lock:
                cur = self.mem.conn.cursor()

                # 🔍 check exists
                cur.execute(
                    "SELECT qty FROM stock WHERE name=?",
                    (name,)
                )
                result = cur.fetchone()

                if result:
                    cur.execute(
                        """
                        UPDATE stock
                        SET qty = qty + ?, price = ?
                        WHERE name = ?
                        """,
                        (qty, price, name)
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO stock(name, qty, price)
                        VALUES(?,?,?)
                        """,
                        (name, qty, price)
                    )

                self.mem.conn.commit()
                return True

        except Exception as e:
            print("[STOCK] add error:", e)
            return False

    # =====================
    # 📊 GET STOCK (SAFE READ)
    # =====================
    def get(self, item):

        try:
            cur = self.mem.conn.cursor()
            cur.execute(
                "SELECT qty FROM stock WHERE name=?",
                (item,)
            )

            result = cur.fetchone()
            return result[0] if result else 0

        except Exception as e:
            print("[STOCK] get error:", e)
            return 0
