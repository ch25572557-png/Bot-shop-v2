import threading

class StockSystem:
    def __init__(self, mem):
        self.mem = mem
        self.lock = threading.Lock()

    # =====================
    # 📦 MINUS STOCK (SAFE + NO NEGATIVE)
    # =====================
    def minus(self, item, amount=1):

        try:
            amount = max(int(amount), 1)
        except:
            amount = 1

        try:
            with self.lock:
                cur = self.mem.conn.cursor()

                # 🔒 safe atomic + prevent negative
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
    # ➕ ADD STOCK (SAFE UPSERT FIXED)
    # =====================
    def add(self, name, qty, price):

        try:
            name = str(name).strip()
            qty = int(qty)
            price = float(price)
        except:
            return False

        if not name or qty <= 0 or price < 0:
            return False

        try:
            with self.lock:
                cur = self.mem.conn.cursor()

                # 🔍 exists check
                cur.execute(
                    "SELECT qty FROM stock WHERE name=?",
                    (name,)
                )
                result = cur.fetchone()

                if result:
                    # ⚠️ only update qty, NOT overwrite price blindly (safer)
                    cur.execute(
                        """
                        UPDATE stock
                        SET qty = qty + ?
                        WHERE name = ?
                        """,
                        (qty, name)
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
    # 📊 GET STOCK (THREAD SAFE READ)
    # =====================
    def get(self, item):

        try:
            with self.lock:
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
