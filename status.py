class StatusSystem:
    def __init__(self, mem):
        self.mem = mem

    # =====================
    # 🔄 SET STATUS (SAFE + UNIFIED)
    # =====================
    def set(self, order_id, status):
        try:
            # 🔥 reuse memory layer (ไม่แตะ cur ตรง)
            self.mem.update_order_status(order_id, status)
            return True
        except Exception as e:
            print("[STATUS] set error:", e)
            return False

    # =====================
    # 📊 GET STATUS (SAFE + NO DIRECT CURSOR)
    # =====================
    def get(self, order_id):
        try:
            data = self.mem.get_order(order_id)

            if not data:
                return None

            # รองรับทั้งโครงเก่า + ใหม่แบบ robust
            try:
                return data[4]  # user,item,amount,roblox,status
            except:
                return data[2]  # fallback legacy

        except Exception as e:
            print("[STATUS] get error:", e)
            return None

    # =====================
    # 🔍 CHECK STATUS GROUP (FINAL RULE SET)
    # =====================
    def is_done(self, order_id):
        status = self.get(order_id)

        if not status:
            return False

        return status in ["DONE", "LOCKED"]

    # =====================
    # 🧠 OPTIONAL: CHECK ACTIVE ORDER
    # =====================
    def is_active(self, order_id):
        status = self.get(order_id)

        if not status:
            return False

        return status not in ["DONE", "LOCKED"]
