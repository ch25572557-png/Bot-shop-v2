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
    # 📦 SAFE GET (CORE)
    # =====================
    def get(self, path, default=None):
        with self._lock:
            return self.config.get(path, default)

    # =====================
    # 🔐 CHANNEL (SAFE INT)
    # =====================
    def channel(self, key):
        with self._lock:
            val = self.config.get_channel(key)

            try:
                return int(val)
            except:
                return None

    # =====================
    # 👑 ROLE (SAFE INT)
    # =====================
    def role(self, key):
        with self._lock:
            val = self.config.get_role(key)

            try:
                return int(val)
            except:
                return None

    # =====================
    # ⚙️ SETTING (SAFE)
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
