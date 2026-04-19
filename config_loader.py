import json
import os

class ConfigLoader:

    def __init__(self, path="config.json"):
        self.path = path
        self.config = {}
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
                self.config = json.load(f)

            print("[CONFIG] ✅ Loaded successfully")

        except Exception as e:
            print(f"[CONFIG] ❌ Load error: {e}")
            self.config = {}

    # =====================
    # 🔄 RELOAD CONFIG
    # =====================
    def reload(self):
        self.load()

    # =====================
    # 🔎 SAFE GET (สำคัญสุด)
    # =====================
    def get(self, path, default=None):
        try:
            keys = path.split(".")
            data = self.config

            for k in keys:
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
