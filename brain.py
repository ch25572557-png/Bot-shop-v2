import json
import threading

class Brain:
    def __init__(self):
        self.data = {}
        self.lock = threading.RLock()
        self.version = 0
        self.reload()

    def reload(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                new_data = json.load(f)

            with self.lock:
                self.data = new_data
                self.version += 1

        except Exception as e:
            print("[BRAIN ERROR] load config failed:", e)

    def get(self, path, default=None):
        v = self.data  # 🔥 no lock during read (faster)

        try:
            for p in path.split("."):
                if isinstance(v, dict) and p in v:
                    v = v[p]
                else:
                    return default
            return v

        except:
            return default
