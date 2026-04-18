class StatusSystem:
    def __init__(self, mem):
        self.mem = mem

    # =====================
    # 🔄 SET STATUS (SAFE)
    # =====================
    def set(self, order_id, status):

        try:
            self.mem.update_order_status(order_id, status)
            return True
        except Exception as e:
            print("[STATUS] set error:", e)
            return False

    # =====================
    # 📊 GET STATUS (SAFE + CLEAN)
    # =====================
    def get(self, order_id):

        try:
            self.mem.cur.execute(
                "SELECT status FROM orders WHERE id=?",
                (order_id,)
            )

            result = self.mem.cur.fetchone()

            if not result:
                return None

            return result[0]

        except Exception as e:
            print("[STATUS] get error:", e)
            return None

    # =====================
    # 🔍 CHECK STATUS GROUP (C FEATURE)
    # =====================
    def is_done(self, order_id):

        status = self.get(order_id)

        if not status:
            return False

        return status in ["DONE", "LOCKED"]
