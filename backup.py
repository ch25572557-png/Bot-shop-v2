import discord
import asyncio


class BackupSystem:

    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

        # 🔥 cache channel ลด API call
        self._channel_cache = None
        self._channel_id = None

    # =====================
    # 🔧 GET CHANNEL (CACHED)
    # =====================
    async def _get_channel(self):

        try:
            ch_id = self.brain.get("CHANNELS.BACKUP")

            if not ch_id:
                return None

            ch_id = int(ch_id)

            # =====================
            # 🔥 CACHE HIT
            # =====================
            if self._channel_cache and self._channel_id == ch_id:
                return self._channel_cache

            channel = self.bot.get_channel(ch_id)

            if channel is None:
                channel = await self.bot.fetch_channel(ch_id)

            # cache update
            self._channel_cache = channel
            self._channel_id = ch_id

            return channel

        except Exception as e:
            print("[BACKUP] channel resolve error:", e)
            return None

    # =====================
    # 💾 CORE LOG (PRO SAFE)
    # =====================
    async def log(self, message):

        channel = await self._get_channel()

        if not channel:
            print("[BACKUP] channel not found")
            return

        try:
            embed = discord.Embed(
                title="💾 BACKUP LOG",
                description=message[:4000],  # 🔥 กัน Discord limit crash
                color=0x95a5a6
            )

            await channel.send(embed=embed)

        except discord.HTTPException as e:
            print("[BACKUP HTTP ERROR]", e)

        except Exception as e:
            print("[BACKUP ERROR]", e)

    # =====================
    # 🛒 ORDER LOG
    # =====================
    async def order(self, order_id, user, item):

        await self.log(
            f"🛒 ORDER #{order_id}\n"
            f"👤 {user}\n"
            f"📦 {item}"
        )

    # =====================
    # ✅ COMPLETE LOG
    # =====================
    async def complete(self, order_id, user, item):

        await self.log(
            f"✅ COMPLETE #{order_id}\n"
            f"👤 {user}\n"
            f"📦 {item}"
        )

    # =====================
    # ❌ CANCEL LOG
    # =====================
    async def cancel(self, order_id, user, item):

        await self.log(
            f"❌ CANCEL #{order_id}\n"
            f"👤 {user}\n"
            f"📦 {item}"
        )

    # =====================
    # ⚠️ ERROR LOG
    # =====================
    async def error(self, message):

        await self.log(f"⚠️ ERROR\n{message}")
