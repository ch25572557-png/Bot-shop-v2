class BackupSystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 🔧 INTERNAL CHANNEL RESOLVE (SAFE + FAST)
    # =====================
    async def _get_channel(self):
        try:
            ch_id = self.brain.get("CHANNELS.BACKUP")
            if not ch_id:
                return None

            ch_id = int(ch_id)

            channel = self.bot.get_channel(ch_id)

            # fallback only if cache miss
            if channel is None:
                channel = await self.bot.fetch_channel(ch_id)

            return channel

        except Exception as e:
            print("[BACKUP] channel resolve error:", e)
            return None

    # =====================
    # 💾 CORE LOG (SAFE)
    # =====================
    async def log(self, message):

        channel = await self._get_channel()
        if not channel:
            print("[BACKUP] channel not found")
            return

        try:
            await channel.send(f"💾 BACKUP\n{message}")

        except Exception as e:
            print("[BACKUP ERROR]", e)

    # =====================
    # 🛒 ORDER LOG
    # =====================
    async def order(self, order_id, user, item):

        try:
            await self.log(f"🛒 ORDER #{order_id} | {user} | {item}")
        except Exception as e:
            print("[BACKUP ORDER ERROR]", e)

    # =====================
    # ✅ COMPLETE LOG
    # =====================
    async def complete(self, order_id, user, item):

        try:
            await self.log(f"✅ COMPLETE #{order_id} | {user} | {item}")
        except Exception as e:
            print("[BACKUP COMPLETE ERROR]", e)

    # =====================
    # ⚠️ ERROR LOG
    # =====================
    async def error(self, message):

        try:
            await self.log(f"⚠️ ERROR\n{message}")
        except Exception as e:
            print("[BACKUP ERROR LOG FAILED]", e)
