import json
import threading

class Brain:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()
        self.reload()

    # =====================
    # 🔄 LOAD CONFIG SAFELY (THREAD SAFE)
    # =====================
    def reload(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                new_data = json.load(f)

            # 🔒 atomic replace
            with self.lock:
                self.data = new_data

        except Exception as e:
            print("[BRAIN ERROR] load config failed:", e)
            with self.lock:
                self.data = {}

    # =====================
    # 🧠 GET VALUE (SAFE + BACKWARD COMPATIBLE)
    # =====================
    def get(self, path, default=None):
        try:
            with self.lock:
                v = self.data

                for p in path.split("."):
                    if isinstance(v, dict) and p in v:
                        v = v[p]
                    else:
                        return default

                return v

        except Exception as e:
            print(f"[BRAIN ERROR] invalid path {path}:", e)
            return default
