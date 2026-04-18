class BackupSystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 💾 GENERAL LOG
    # =====================
    async def log(self, message):

        try:
            ch_id = self.brain.get("CHANNELS.BACKUP")
            channel = self.bot.get_channel(int(ch_id))

            if channel is None:
                print("[BACKUP] Channel not found")
                return

            await channel.send(f"💾 BACKUP\n{message}")

        except Exception as e:
            print(f"[BACKUP ERROR] {e}")

    # =====================
    # 🛒 ORDER LOG
    # =====================
    async def order(self, order_id, user, item):

        msg = f"🛒 ORDER #{order_id} | {user} | {item}"
        await self.log(msg)

    # =====================
    # ✅ COMPLETE LOG
    # =====================
    async def complete(self, order_id, user, item):

        msg = f"✅ COMPLETE #{order_id} | {user} | {item}"
        await self.log(msg)

    # =====================
    # ⚠️ ERROR LOG
    # =====================
    async def error(self, message):

        msg = f"⚠️ ERROR\n{message}"
        await self.log(msg)
