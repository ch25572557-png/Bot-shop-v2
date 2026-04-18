import discord
from status_view import StatusView

class TicketSystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 📢 ADMIN SEND (SAFE)
    # =====================
    async def send_to_admin(self, guild, message: str):
        try:
            ch_id = self.brain.get("CHANNELS.ORDER_NOTIFY")
            if not ch_id:
                return

            try:
                channel = self.bot.get_channel(int(ch_id))
                if channel is None:
                    channel = await self.bot.fetch_channel(int(ch_id))
            except:
                return

            if channel:
                await channel.send(message)

        except:
            pass

    # =====================
    # 🎫 CREATE TICKET
    # =====================
    async def create(self, guild, user, order_id):

        category = None

        # =====================
        # 📁 CATEGORY SAFE
        # =====================
        try:
            category_id = self.brain.get("CHANNELS.TICKET_CATEGORY")

            if category_id:
                try:
                    ch = guild.get_channel(int(category_id))
                    if isinstance(ch, discord.CategoryChannel):
                        category = ch
                    else:
                        ch = await guild.fetch_channel(int(category_id))
                        if isinstance(ch, discord.CategoryChannel):
                            category = ch
                except:
                    category = None

        except:
            category = None

        # =====================
        # 🔒 PERMISSION SAFE
        # =====================
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
        except:
            return None

        # =====================
        # 🧱 CREATE CHANNEL
        # =====================
        try:
            channel = await guild.create_text_channel(
                name=f"ticket-{order_id}-{user.name}",
                category=category,
                overwrites=overwrites
            )
        except:
            return None

        # =====================
        # 💾 SAVE TICKET
        # =====================
        try:
            self.bot.mem.save_ticket(order_id, str(channel.id))
        except:
            pass

        # =====================
        # 📦 ORDER LOAD SAFE
        # =====================
        item = "Unknown"
        amount = 1
        roblox_user = None

        try:
            data = self.bot.mem.get_order(order_id)
            if data:
                data = list(data) + [None]*5
                _, item, amount, roblox_user, _ = data[:5]
        except:
            pass

        # =====================
        # 📢 ADMIN NOTIFY
        # =====================
        await self.send_to_admin(
            guild,
            f"🆕 ORDER #{order_id}\n"
            f"👤 {user}\n"
            f"📦 {item} x{amount}"
        )

        # =====================
        # 📢 TICKET MESSAGE
        # =====================
        try:
            msg = (
                f"🎫 ORDER #{order_id}\n"
                f"👤 {user.mention}\n"
                f"📦 {item} x{amount}\n"
            )

            if roblox_user:
                msg += f"🎮 Roblox: {roblox_user}\n"

            msg += "\n⚙️ ใช้ปุ่มด้านล่างเพื่ออัปเดตสถานะ"

            await channel.send(
                msg,
                view=StatusView(self.bot, order_id)
            )

        except:
            pass

        return channel
