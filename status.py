class StatusSystem:
    def __init__(self, mem):
        self.mem = mem

    # =====================
    # 🔄 SET STATUS
    # =====================
    def set(self, order_id, status):
        try:
            return self.mem.update_order_status(order_id, status)
        except Exception as e:
            print("[STATUS] set error:", e)
            return False

    # =====================
    # 📊 GET STATUS (FIXED BUG)
    # =====================
    def get(self, order_id):
        try:
            data = self.mem.get_order(order_id)
            if not data:
                return None

            # ✅ FIX: schema ชัดเจน (index 4 = status)
            return data[4]

        except Exception as e:
            print("[STATUS] get error:", e)
            return None

    # =====================
    # 🔍 DONE CHECK
    # =====================
    def is_done(self, order_id):
        status = self.get(order_id)
        return status in ("DONE", "LOCKED")

    # =====================
    # 🧠 ACTIVE CHECK
    # =====================
    def is_active(self, order_id):
        status = self.get(order_id)
        return status not in ("DONE", "LOCKED")
