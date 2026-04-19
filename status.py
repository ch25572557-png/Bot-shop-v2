class StatusSystem:
    def __init__(self, mem):
        self.mem = mem

    # =====================
    # 🔄 SET STATUS (FIX)
    # =====================
    def set(self, order_id, status):
        try:
            self.mem.update_order_status(order_id, status)
            return True
        except Exception as e:
            print("[STATUS] set error:", e)
            return False

    # =====================
    # 📊 GET STATUS
    # =====================
    def get(self, order_id):
        try:
            data = self.mem.get_order(order_id)

            if not data:
                return None

            return data[4]

        except Exception as e:
            print("[STATUS] get error:", e)
            return None

    # =====================
    # 🔍 DONE CHECK (SAFE)
    # =====================
    def is_done(self, order_id):
        status = self.get(order_id)

        if not status:
            return False

        return status in ("DONE", "LOCKED")

    # =====================
    # 🧠 ACTIVE CHECK (FIX)
    # =====================
    def is_active(self, order_id):
        status = self.get(order_id)

        if not status:
            return False

        return status not in ("DONE", "LOCKED", "CANCELLED")
