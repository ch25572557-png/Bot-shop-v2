import json

class Brain:
    def __init__(self):
        self.data = {}
        self.reload()

    # =====================
    # 🔄 LOAD CONFIG SAFELY
    # =====================
    def reload(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception as e:
            print("[BRAIN ERROR] load config failed:", e)
            self.data = {}

    # =====================
    # 🧠 GET VALUE (SAFE)
    # =====================
    def get(self, path, default=None):
        try:
            v = self.data
            for p in path.split("."):
                if isinstance(v, dict):
                    v = v[p]
                else:
                    return default
            return v
        except Exception as e:
            print(f"[BRAIN ERROR] invalid path {path}:", e)
            return default
