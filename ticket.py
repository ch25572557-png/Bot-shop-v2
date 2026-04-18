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
        # 💾 SAVE LINK
        # =====================
        try:
            self.bot.mem.save_ticket(order_id, str(channel.id))
        except:
            pass

        # =====================
        # 📦 GET ORDER DATA
        # =====================
        try:
            data = self.bot.mem.get_order(order_id)
        except:
            data = None

        # 🧠 รองรับของเก่า + ใหม่
        if data:
            try:
                user_db, item, amount, roblox_user, status = data
            except:
                user_db, item, status = data
                amount = 1
                roblox_user = None
        else:
            item = "Unknown"
            amount = 1
            roblox_user = None

        # =====================
        # 📢 SEND MESSAGE
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
