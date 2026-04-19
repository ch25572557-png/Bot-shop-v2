import asyncio


class StockAlertSystem:

    def __init__(self, bot):
        self.bot = bot
        self.running = False
        self.last_state = {}

    def start(self):
        if self.running:
            return

        self.running = True
        self.bot.loop.create_task(self.loop())
        print("[STOCK ALERT] started (V2)")

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
    # 📦 CHECK STOCK (🔥 FIX)
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
        # 🔥 CHANNEL
        # =====================
        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
        except:
            channel = None

        if not channel:
            print("[STOCK ALERT] channel not found")
            return

        # =====================
        # 📦 GET STOCK (V2 ONLY)
        # =====================
        try:
            data = await self.bot.mem.get_all_stock()
        except Exception as e:
            print("[STOCK FETCH ERROR]", e)
            return

        alerts = []

        for name, qty in data:

            prev = self.last_state.get(name)
            is_low = qty <= low_limit

            # แจ้งเฉพาะตอนเปลี่ยนสถานะ
            if prev == is_low:
                continue

            self.last_state[name] = is_low

            if is_low:
                alerts.append(f"⚠️ {name} เหลือ {qty}")

        # =====================
        # 📢 SEND
        # =====================
        if alerts:

            role_ping = f"<@&{role_id}>" if role_id else ""

            msg = (
                f"🚨 **STOCK ALERT** {role_ping}\n\n"
                + "\n".join(alerts)
            )

            try:
                await channel.send(msg)
            except Exception as e:
                print("[SEND ERROR]", e)

    # =====================
    # 🔄 RESET
    # =====================
    def reset_item(self, item):
        self.last_state.pop(item, None)
