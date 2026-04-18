import json
import threading

class Brain:
    def __init__(self):
        self._lock = threading.RLock()
        self._data = {}
        self._version = 0
        self.reload()

    def reload(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                new_data = json.load(f)

            with self._lock:
                self._data = new_data
                self._version += 1

        except Exception as e:
            print("[BRAIN ERROR] load config failed:", e)

    def get(self, path, default=None):
        try:
            data = self._data

            for key in path.split("."):
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    return default

            return data

        except:
            return default

    # 🔥 FIX: rename method
    def get_version(self):
        return self._version
