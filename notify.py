import discord


class NotifySystem:

    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 🔧 GET CHANNEL (FULL SAFE FIX)
    # =====================
    async def _get_channel(self):

        try:
            ch_id = self.brain.channel("ORDER_NOTIFY")
            if not ch_id:
                return None

            # 🔥 FIX: force int
            try:
                ch_id = int(ch_id)
            except:
                return None

            channel = self.bot.get_channel(ch_id)

            if channel is None:
                channel = await self.bot.fetch_channel(ch_id)

            return channel

        except Exception as e:
            print("[NOTIFY] channel error:", e)
            return None

    # =====================
    # 🔔 NEW ORDER
    # =====================
    async def admin(self, user, item, order_id=None):

        ch = await self._get_channel()
        if not ch:
            return

        try:
            role_id = self.brain.role("ADMIN_ROLE")

            embed = discord.Embed(
                title="🔔 NEW ORDER",
                color=0x00ffcc
            )

            embed.add_field(
                name="👤 User",
                value=getattr(user, "mention", str(user)),
                inline=False
            )

            embed.add_field(
                name="📦 Item",
                value=item,
                inline=False
            )

            if order_id:
                embed.add_field(
                    name="🆔 Order ID",
                    value=str(order_id),
                    inline=False
                )

            content = None
            if role_id:
                try:
                    content = f"<@&{int(role_id)}>"
                except:
                    content = None

            await ch.send(content=content, embed=embed)

        except Exception as e:
            print("[NOTIFY] admin error:", e)

    # =====================
    # ✅ COMPLETE
    # =====================
    async def complete(self, user, item, order_id=None):

        ch = await self._get_channel()
        if not ch:
            return

        try:
            embed = discord.Embed(
                title="✅ ORDER COMPLETE",
                color=0x00ff00
            )

            embed.add_field(
                name="👤 User",
                value=getattr(user, "mention", str(user)),
                inline=False
            )

            embed.add_field(
                name="📦 Item",
                value=item,
                inline=False
            )

            if order_id:
                embed.add_field(
                    name="🆔 Order ID",
                    value=str(order_id),
                    inline=False
                )

            await ch.send(embed=embed)

        except Exception as e:
            print("[NOTIFY] complete error:", e)

    # =====================
    # ⚠️ STOCK ALERT
    # =====================
    async def stock_alert(self, item, qty):

        ch = await self._get_channel()
        if not ch:
            return

        try:
            role_id = self.brain.role("ADMIN_ROLE")

            embed = discord.Embed(
                title="⚠️ STOCK ALERT",
                color=0xff0000
            )

            embed.add_field(name="📦 Item", value=item, inline=False)
            embed.add_field(name="📉 Remaining", value=str(qty), inline=False)

            content = None
            if role_id:
                try:
                    content = f"<@&{int(role_id)}>"
                except:
                    content = None

            await ch.send(content=content, embed=embed)

        except Exception as e:
            print("[NOTIFY] stock alert error:", e)
