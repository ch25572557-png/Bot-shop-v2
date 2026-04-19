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

            if not isinstance(data, dict):
                raise ValueError("config must be dict")

            with self._lock:
                self.config = data
                self.version += 1

            print(f"[CONFIG] ✅ Loaded v{self.version}")

        except Exception as e:
            print(f"[CONFIG] ❌ Load error: {e}")
            self.config = {}

    # =====================
    # 🔄 RELOAD
    # =====================
    def reload(self):
        self.load()

    # =====================
    # 🔎 SAFE GET (FIXED)
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

        except:
            return default

    # =====================
    # 🔐 CHANNEL (SAFE)
    # =====================
    def get_channel(self, key):
        val = self.get(f"CHANNELS.{key}")

        if not val:
            return None

        try:
            return int(val)
        except:
            return None

    # =====================
    # 🔐 ROLE (SAFE)
    # =====================
    def get_role(self, key):
        val = self.get(f"ROLES.{key}")

        if not val:
            return None

        try:
            return int(val)
        except:
            return None

    # =====================
    # ⚙️ SETTING (SAFE)
    # =====================
    def get_setting(self, key, default=None):
        val = self.get(f"SETTINGS.{key}", default)
        return default if val is None else val

    # =====================
    # 🔢 VERSION
    # =====================
    def get_version(self):
        return self.version
