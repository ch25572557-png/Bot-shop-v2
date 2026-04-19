import json
import os
import threading


class ConfigLoader:

    def __init__(self, path="config.json"):
        self.path = path
        self.config = {}
        self._lock = threading.RLock()
        self.version = 0
        self.load()

    # =====================
    # 📥 LOAD CONFIG
    # =====================
    def load(self):
        try:
            if not os.path.exists(self.path):
                print("[CONFIG] ❌ config.json not found")
                self.config = {}
                return

            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)

            with self._lock:
                self.config = data
                self.version += 1

            print(f"[CONFIG] ✅ Loaded v{self.version}")

        except Exception as e:
            print(f"[CONFIG] ❌ Load error: {e}")
            self.config = {}

    # =====================
    # 🔄 RELOAD CONFIG
    # =====================
    def reload(self):
        self.load()

    # =====================
    # 🔎 SAFE GET (ROBUST)
    # =====================
    def get(self, path, default=None):
        try:
            keys = path.split(".")
            data = self.config

            for k in keys:

                if not isinstance(data, dict):
                    return default

                if k not in data:
                    return default

                data = data[k]

            return data

        except Exception:
            return default

    # =====================
    # 🔐 GET CHANNEL
    # =====================
    def get_channel(self, key):
        return self.get(f"CHANNELS.{key}")

    # =====================
    # 🔐 GET ROLE
    # =====================
    def get_role(self, key):
        return self.get(f"ROLES.{key}")

    # =====================
    # ⚙️ GET SETTING
    # =====================
    def get_setting(self, key, default=None):
        return self.get(f"SETTINGS.{key}", default)

    # =====================
    # 🔢 VERSION
    # =====================
    def get_version(self):
        return self.version
