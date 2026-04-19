import asyncio
from utils import safe_db_execute


class DashboardWorker:

    def __init__(self, bot):
        self.bot = bot
        self.running = False

        # 🔥 persist message id (กันหายหลัง restart)
        self.message_id = None

    # =====================
    # 🚀 START
    # =====================
    def start(self):
        if self.running:
            return

        self.running = True

        try:
            self.bot.loop.create_task(self.loop())
            print("[DASHBOARD] started")
        except Exception as e:
            print("[DASHBOARD START ERROR]", e)

    # =====================
    # 🔁 LOOP
    # =====================
    async def loop(self):

        await asyncio.sleep(3)  # 🔥 รอ bot ready ก่อน

        while self.running:
            try:
                await self.update_dashboard()
            except Exception as e:
                print("[DASHBOARD LOOP ERROR]", e)

            delay = self.bot.brain.setting("DASHBOARD_AUTO_UPDATE_SEC", 10)

            try:
                delay = max(int(delay), 5)
            except:
                delay = 10

            await asyncio.sleep(delay)

    # =====================
    # 📊 BUILD TEXT
    # =====================
    def build_text(self):

        stock_data = safe_db_execute(
            self.bot.mem.conn,
            "SELECT name, qty FROM stock"
        ) or []

        order_data = safe_db_execute(
            self.bot.mem.conn,
            "SELECT id, item, amount, status FROM orders ORDER BY id DESC LIMIT 5"
        ) or []

        stock_text = "\n".join(
            [f"📦 {n} = {q}" for n, q in stock_data]
        ) or "No stock"

        order_text = "\n".join(
            [f"#{o[0]} {o[1]} x{o[2]} ({o[3]})" for o in order_data]
        ) or "No orders"

        return (
            "🧠 **DASHBOARD LIVE**\n\n"
            "📦 STOCK\n"
            f"{stock_text}\n\n"
            "📊 ORDERS\n"
            f"{order_text}\n"
        )

    # =====================
    # 📤 UPDATE
    # =====================
    async def update_dashboard(self):

        channel_id = self.bot.brain.channel("DASHBOARD_CHANNEL")
        if not channel_id:
            return

        # =====================
        # 🔥 SAFE CHANNEL
        # =====================
        try:
            channel = self.bot.get_channel(channel_id)

            if not channel:
                channel = await self.bot.fetch_channel(channel_id)

        except Exception as e:
            print("[DASHBOARD CHANNEL ERROR]", e)
            return

        content = self.build_text()

        # =====================
        # 🔥 LOAD SAVED MESSAGE ID (ครั้งแรก)
        # =====================
        if not self.message_id:
            try:
                self.message_id = self.bot.brain.setting("DASHBOARD_MESSAGE_ID")
            except:
                self.message_id = None

        try:

            # =====================
            # ✏️ EDIT MESSAGE
            # =====================
            if self.message_id:

                try:
                    msg = await channel.fetch_message(int(self.message_id))
                    await msg.edit(content=content)
                    return

                except:
                    print("[DASHBOARD] message lost, recreating...")
                    self.message_id = None

            # =====================
            # 🆕 CREATE NEW
            # =====================
            msg = await channel.send(content)
            self.message_id = msg.id

            # 🔥 save id ลง config (ถ้ามีระบบ save)
            try:
                print(f"[DASHBOARD] new message id = {self.message_id}")
            except:
                pass

        except Exception as e:
            print("[DASHBOARD UPDATE ERROR]", e)
            self.message_id = None
