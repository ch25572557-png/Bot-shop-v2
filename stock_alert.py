import asyncio
from utils import safe_send, safe_db_execute


class StockAlertSystem:

    def __init__(self, bot):
        self.bot = bot

        self.running = False

        # 🔥 เก็บ state แบบ smarter
        self.last_state = {}

    # =====================
    # 🚀 START LOOP
    # =====================
    def start(self):
        if self.running:
            return

        self.running = True

        try:
            self.bot.loop.create_task(self.loop())
            print("[STOCK ALERT] started")

        except Exception as e:
            print("[STOCK ALERT START ERROR]", e)

    # =====================
    # 🔁 MAIN LOOP
    # =====================
    async def loop(self):

        while self.running:

            try:
                await self.check_stock()

            except Exception as e:
                print("[STOCK ALERT LOOP ERROR]", e)

            cooldown = self.bot.brain.setting("STOCK_ALERT_COOLDOWN_SEC", 60)

            try:
                cooldown = int(cooldown)
            except:
                cooldown = 60

            await asyncio.sleep(cooldown)

    # =====================
    # 📦 CHECK STOCK
    # =====================
    async def check_stock(self):

        low_limit = self.bot.brain.setting("LOW_STOCK", 100)

        try:
            low_limit = int(low_limit)
        except:
            low_limit = 100

        channel_id = self.bot.brain.channel("STOCK_ALERT_CHANNEL")
        role_id = self.bot.brain.role("ADMIN_ROLE")

        # =====================
        # 🔥 SAFE CHANNEL FETCH
        # =====================
        try:
            channel = self.bot.get_channel(int(channel_id)) if channel_id else None

            if not channel:
                channel = await self.bot.fetch_channel(int(channel_id))

        except:
            channel = None

        if not channel:
            print("[STOCK ALERT] channel not found")
            return

        # =====================
        # 📦 GET STOCK
        # =====================
        data = safe_db_execute(
            self.bot.mem.conn,
            "SELECT name, qty FROM stock"
        )

        if not data:
            return

        alerts = []

        for name, qty in data:

            # =====================
            # 🔥 STATE CHANGE DETECTION (FIX)
            # =====================
            prev = self.last_state.get(name)

            is_low = qty <= low_limit

            # แจ้งเฉพาะ "เปลี่ยนสถานะ"
            if prev == is_low:
                continue

            self.last_state[name] = is_low

            if is_low:
                alerts.append(f"⚠️ {name} เหลือ {qty}")

        # =====================
        # 📢 SEND ALERT
        # =====================
        if alerts:

            role_ping = f"<@&{role_id}>" if role_id else ""

            msg = (
                f"🚨 **STOCK ALERT** {role_ping}\n\n"
                + "\n".join(alerts)
            )

            await safe_send(channel, content=msg)

    # =====================
    # 🔄 RESET (CALL FROM RESTOCK IF WANT)
    # =====================
    def reset_item(self, item):
        self.last_state.pop(item, None)
