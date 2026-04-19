import asyncio
from utils import safe_send, safe_db_execute


class StockAlertSystem:

    def __init__(self, bot):
        self.bot = bot

        self.running = False
        self.last_alert = {}

    # =====================
    # 🚀 START LOOP (SAFE)
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

        # 🔥 safe convert
        try:
            channel = self.bot.get_channel(int(channel_id)) if channel_id else None
        except:
            channel = None

        if not channel:
            print("[STOCK ALERT] channel not found")
            return

        data = safe_db_execute(
            self.bot.mem.conn,
            "SELECT name, qty FROM stock"
        )

        if not data:
            return

        alerts = []

        for item in data:

            name = item[0]
            qty = item[1]

            if qty <= low_limit:

                # กัน spam ซ้ำ
                if self.last_alert.get(name) == qty:
                    continue

                self.last_alert[name] = qty
                alerts.append(f"⚠️ {name} เหลือ {qty}")

        if alerts:

            role_ping = f"<@&{role_id}>" if role_id else ""

            msg = (
                f"🚨 **STOCK ALERT** {role_ping}\n\n"
                + "\n".join(alerts)
            )

            await safe_send(channel, content=msg)
