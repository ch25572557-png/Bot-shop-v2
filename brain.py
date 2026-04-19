import threading
from config_loader import ConfigLoader


class Brain:

    def __init__(self):
        self._lock = threading.RLock()
        self._version = 0

        self.config = ConfigLoader()

    # =====================
    # 🔄 RELOAD CONFIG
    # =====================
    def reload(self):
        with self._lock:
            self.config.reload()
            self._version += 1
            print(f"[BRAIN] config reloaded v{self._version}")

    # =====================
    # 📦 SAFE GET
    # =====================
    def get(self, path, default=None):
        with self._lock:
            return self.config.get(path, default)

    # =====================
    # 🔐 CHANNEL (DEBUG SAFE)
    # =====================
    def channel(self, key):
        with self._lock:
            val = self.config.get_channel(key)

            if not val:
                print(f"[BRAIN WARNING] channel {key} not found")
                return None

            try:
                return int(val)
            except Exception:
                print(f"[BRAIN ERROR] invalid channel id: {key} = {val}")
                return None

    # =====================
    # 👑 ROLE (DEBUG SAFE)
    # =====================
    def role(self, key):
        with self._lock:
            val = self.config.get_role(key)

            if not val:
                print(f"[BRAIN WARNING] role {key} not found")
                return None

            try:
                return int(val)
            except Exception:
                print(f"[BRAIN ERROR] invalid role id: {key} = {val}")
                return None

    # =====================
    # ⚙️ SETTING
    # =====================
    def setting(self, key, default=None):
        with self._lock:
            return self.config.get_setting(key, default)

    # =====================
    # 🔢 VERSION
    # =====================
    def get_version(self):
        return self._version

    # =====================
    # 🔁 FORCE RELOAD
    # =====================
    def force_reload(self):
        with self._lock:
            self.config.reload()
            self._version += 1
            print(f"[BRAIN] force reload v{self._version}")
