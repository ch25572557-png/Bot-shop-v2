import discord
from status_view import StatusView

class TicketSystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    async def create(self, guild, user, order_id):

        # =====================
        # 📁 GET CATEGORY
        # =====================
        try:
            category_id = int(self.brain.get("CHANNELS.TICKET_CATEGORY"))
            category = guild.get_channel(category_id)
        except:
            category = None

        # =====================
        # 🔒 PERMISSION
        # =====================
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

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
        # 💾 SAVE LINK (ใช้ mem function)
        # =====================
        try:
            self.bot.mem.save_ticket(order_id, str(channel.id))
        except:
            pass

        # =====================
        # 📢 SEND MESSAGE + BUTTON
        # =====================
        try:
            await channel.send(
                f"🎫 Ticket for ORDER #{order_id}\n"
                f"👤 {user.mention}",
                view=StatusView(self.bot, order_id)
            )
        except:
            pass

        return channel
