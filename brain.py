import threading
from config_loader import ConfigLoader

class Brain:

    def __init__(self):
        self._lock = threading.RLock()
        self._version = 0

        # 🔥 ใช้ config_loader แทนอ่าน json ตรง
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
    # 🔐 CHANNEL SHORTCUT
    # =====================
    def channel(self, key):
        return self.config.get_channel(key)

    # =====================
    # 🔐 ROLE SHORTCUT
    # =====================
    def role(self, key):
        return self.config.get_role(key)

    # =====================
    # ⚙️ SETTING SHORTCUT
    # =====================
    def setting(self, key, default=None):
        return self.config.get_setting(key, default)

    # =====================
    # 🔢 VERSION
    # =====================
    def get_version(self):
        return self._version
