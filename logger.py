import datetime

class Logger:

    def __init__(self, name="BOT"):
        self.name = name

    def _log(self, level, message):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{self.name}] [{level}] {message}")

    def info(self, msg):
        self._log("INFO", msg)

    def warn(self, msg):
        self._log("WARN", msg)

    def error(self, msg):
        self._log("ERROR", msg)

    def debug(self, msg):
        self._log("DEBUG", msg)


# 🔥 global logger ใช้ง่าย
log = Logger()
