import json
import threading
import os

class Brain:
    def __init__(self):
        self._lock = threading.RLock()
        self._data = {}
        self._version = 0

        self.config_path = "config.json"
        self.reload()

    # =====================
    # 🔄 SAFE RELOAD CONFIG
    # =====================
    def reload(self):

        try:
            if not os.path.exists(self.config_path):
                print("[BRAIN] config.json not found")
                return

            with open(self.config_path, "r", encoding="utf-8") as f:
                new_data = json.load(f)

            with self._lock:
                self._data = new_data
                self._version += 1

            print(f"[BRAIN] config reloaded v{self._version}")

        except json.JSONDecodeError as e:
            # ❌ กัน config พังแล้ว bot ล่ม
            print("[BRAIN ERROR] JSON invalid:", e)

        except Exception as e:
            print("[BRAIN ERROR] load failed:", e)

    # =====================
    # 📦 SAFE GET (THREAD SAFE)
    # =====================
    def get(self, path, default=None):

        try:
            with self._lock:
                data = self._data

                for key in path.split("."):
                    if isinstance(data, dict) and key in data:
                        data = data[key]
                    else:
                        return default

                return data

        except:
            return default

    # =====================
    # 🔢 VERSION TRACKER
    # =====================
    def get_version(self):
        return self._version

    # =====================
    # 🔁 HOT RELOAD (SAFE EXTERNAL CALL)
    # =====================
    def force_reload(self):
        self.reload()
