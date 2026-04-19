import asyncio
from utils import safe_send, safe_db_execute


class DashboardWorker:

    def __init__(self, bot):
        self.bot = bot
        self.running = False
        self.message_id = None

    # =====================
    # 🚀 START
    # =====================
    def start(self):
        if self.running:
            return

        self.running = True
        self.bot.loop.create_task(self.loop())
        print("[DASHBOARD] started")

    # =====================
    # 🔁 MAIN LOOP
    # =====================
    async def loop(self):

        while self.running:

            try:
                await self.update_dashboard()

            except Exception as e:
                print("[DASHBOARD ERROR]", e)

            delay = self.bot.brain.setting("DASHBOARD_AUTO_UPDATE_SEC", 10)

            try:
                delay = int(delay)
            except:
                delay = 10

            await asyncio.sleep(delay)

    # =====================
    # 📊 BUILD DASHBOARD TEXT
    # =====================
    def build_text(self):

        # STOCK
        stock_data = safe_db_execute(
            self.bot.mem.conn,
            "SELECT name, qty FROM stock"
        ) or []

        stock_text = "\n".join(
            [f"📦 {n} = {q}" for n, q in stock_data]
        ) or "No stock"

        # ORDERS
        order_data = safe_db_execute(
            self.bot.mem.conn,
            "SELECT id, item, amount, status FROM orders ORDER BY id DESC LIMIT 5"
        ) or []

        order_text = "\n".join(
            [f"#{o[0]} {o[1]} x{o[2]} ({o[3]})" for o in order_data]
        ) or "No orders"

        text = (
            "🧠 **DASHBOARD LIVE**\n\n"
            "📦 STOCK\n"
            f"{stock_text}\n\n"
            "📊 ORDERS\n"
            f"{order_text}\n"
        )

        return text

    # =====================
    # 📤 UPDATE MESSAGE
    # =====================
    async def update_dashboard(self):

        channel_id = self.bot.brain.channel("DASHBOARD_CHANNEL")

        if not channel_id:
            return

        channel = self.bot.get_channel(int(channel_id))

        if not channel:
            return

        content = self.build_text()

        try:
            # 🔥 ถ้ายังไม่มี message → ส่งใหม่
            if not self.message_id:

                msg = await channel.send(content)
                self.message_id = msg.id

            else:
                msg = await channel.fetch_message(self.message_id)
                await msg.edit(content=content)

        except Exception as e:
            print("[DASHBOARD UPDATE ERROR]", e)

            # fallback: reset message
            self.message_id = None
