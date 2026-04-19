import threading
from config_loader import ConfigLoader

class Brain:

    def __init__(self):
        self._lock = threading.RLock()
        self._version = 0

        # 📦 central config
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
    # 📦 SAFE GET (CORE)
    # =====================
    def get(self, path, default=None):
        with self._lock:
            return self.config.get(path, default)

    # =====================
    # 🔐 CHANNEL (LOCKED)
    # =====================
    def channel(self, key):
        with self._lock:
            return self.config.get_channel(key)

    # =====================
    # 👑 ROLE (LOCKED)
    # =====================
    def role(self, key):
        with self._lock:
            return self.config.get_role(key)

    # =====================
    # ⚙️ SETTING (LOCKED)
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
    # 🔁 FORCE RELOAD (SAFE)
    # =====================
    def force_reload(self):
        with self._lock:
            self.config.reload()
            self._version += 1
            print(f"[BRAIN] force reload v{self._version}")
