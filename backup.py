class BackupSystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 💾 CORE LOG (SAFE)
    # =====================
    async def log(self, message):

        try:
            ch_id = self.brain.get("CHANNELS.BACKUP")

            if not ch_id:
                print("[BACKUP] missing channel id")
                return

            channel = self.bot.get_channel(int(ch_id))

            # fallback
            if channel is None:
                channel = await self.bot.fetch_channel(int(ch_id))

            if channel is None:
                print("[BACKUP] channel not found")
                return

            await channel.send(f"💾 BACKUP\n{message}")

        except Exception as e:
            print(f"[BACKUP ERROR] {e}")

    # =====================
    # 🛒 ORDER LOG
    # =====================
    async def order(self, order_id, user, item):

        try:
            msg = f"🛒 ORDER #{order_id} | {user} | {item}"
            await self.log(msg)
        except Exception as e:
            print("[BACKUP ORDER ERROR]", e)

    # =====================
    # ✅ COMPLETE LOG
    # =====================
    async def complete(self, order_id, user, item):

        try:
            msg = f"✅ COMPLETE #{order_id} | {user} | {item}"
            await self.log(msg)
        except Exception as e:
            print("[BACKUP COMPLETE ERROR]", e)

    # =====================
    # ⚠️ ERROR LOG
    # =====================
    async def error(self, message):

        try:
            msg = f"⚠️ ERROR\n{message}"
            await self.log(msg)
        except Exception as e:
            print("[BACKUP ERROR LOG FAILED]", e)
