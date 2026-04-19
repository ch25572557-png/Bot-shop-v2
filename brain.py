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
        self.config.reload()
        with self._lock:
            self._version += 1
            print(f"[BRAIN] config reloaded v{self._version}")

    # =====================
    # 📦 SAFE GET
    # =====================
    def get(self, path, default=None):
        with self._lock:
            try:
                return self.config.get(path, default)
            except Exception as e:
                print("[BRAIN GET ERROR]", e)
                return default

    # =====================
    # 🔐 CHANNEL
    # =====================
    def channel(self, key):
        with self._lock:
            val = self.config.get_channel(key)

        if val is None:
            print(f"[BRAIN WARNING] CHANNELS.{key} not found")
            return None

        try:
            return int(val)
        except Exception:
            print(f"[BRAIN ERROR] invalid channel id: CHANNELS.{key} = {val}")
            return None

    # =====================
    # 👑 ROLE
    # =====================
    def role(self, key):
        with self._lock:
            val = self.config.get_role(key)

        if val is None:
            print(f"[BRAIN WARNING] ROLES.{key} not found")
            return None

        try:
            return int(val)
        except Exception:
            print(f"[BRAIN ERROR] invalid role id: ROLES.{key} = {val}")
            return None

    # =====================
    # ⚙️ SETTING
    # =====================
    def setting(self, key, default=None):
        with self._lock:
            try:
                val = self.config.get_setting(key, default)
                return default if val is None else val
            except Exception as e:
                print("[BRAIN SETTING ERROR]", e)
                return default

    # =====================
    # 🔢 VERSION
    # =====================
    def get_version(self):
        with self._lock:
            return self._version

    # =====================
    # 🔁 FORCE RELOAD
    # =====================
    def force_reload(self):
        self.config.reload()
        with self._lock:
            self._version += 1
            print(f"[BRAIN] force reload v{self._version}")

    # =====================
    # 🧠 DEBUG FULL (เพิ่มแต่ไม่ลบของเดิม)
    # =====================
    def debug_all(self):
        with self._lock:
            try:
                print("===== BRAIN DEBUG =====")
                print("CHANNELS:", getattr(self.config, "channels", None))
                print("ROLES:", getattr(self.config, "roles", None))
                print("SETTINGS:", getattr(self.config, "settings", None))
                print("=======================")
            except Exception as e:
                print("[BRAIN DEBUG ERROR]", e)
