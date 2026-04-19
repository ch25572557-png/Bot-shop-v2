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
                with self._lock:
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
            with self._lock:
                self.config = {}

    # =====================
    # 🔄 RELOAD
    # =====================
    def reload(self):
        self.load()

    # =====================
    # 🔎 SAFE GET (THREAD SAFE + DEBUG)
    # =====================
    def get(self, path, default=None):
        with self._lock:
            try:
                keys = path.split(".")
                data = self.config

                for k in keys:

                    if not isinstance(data, dict):
                        print(f"[CONFIG] ⚠️ Path broken at {k} ({path})")
                        return default

                    if k not in data:
                        # 🔥 debug สำคัญมาก
                        print(f"[CONFIG] ⚠️ Missing key: {path}")
                        return default

                    data = data[k]

                return data

            except Exception as e:
                print(f"[CONFIG] ❌ Get error ({path}): {e}")
                return default

    # =====================
    # 🔐 CHANNEL (SAFE INT)
    # =====================
    def get_channel(self, key):
        val = self.get(f"CHANNELS.{key}")

        try:
            return int(val)
        except:
            print(f"[CONFIG] ⚠️ Invalid channel ID: {key} = {val}")
            return None

    # =====================
    # 🔐 ROLE (SAFE INT)
    # =====================
    def get_role(self, key):
        val = self.get(f"ROLES.{key}")

        try:
            return int(val)
        except:
            print(f"[CONFIG] ⚠️ Invalid role ID: {key} = {val}")
            return None

    # =====================
    # ⚙️ SETTING
    # =====================
    def get_setting(self, key, default=None):
        return self.get(f"SETTINGS.{key}", default)

    # =====================
    # 🔢 VERSION
    # =====================
    def get_version(self):
        return self.version
