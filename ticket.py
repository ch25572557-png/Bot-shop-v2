import discord
from status_view import StatusView

class TicketSystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 🎫 CREATE TICKET
    # =====================
    async def create(self, guild, user, order_id):

        # =====================
        # 📁 CATEGORY SAFE
        # =====================
        category = None

        try:
            category_id = self.brain.get("CHANNELS.TICKET_CATEGORY")
            if category_id:
                category = guild.get_channel(int(category_id))

            if not category:
                category = await guild.fetch_channel(int(category_id))

        except:
            category = None

        # =====================
        # 🔒 PERMISSIONS
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
        except Exception as e:
            print("[TICKET] create error:", e)
            return None

        # =====================
        # 💾 SAVE TICKET LINK
        # =====================
        try:
            self.bot.mem.save_ticket(order_id, str(channel.id))
        except Exception as e:
            print("[TICKET] save error:", e)

        # =====================
        # 📦 ORDER DATA
        # =====================
        data = self.bot.mem.get_order(order_id)

        item = "Unknown"
        amount = 1
        roblox_user = None

        if data:
            try:
                user_db, item, amount, roblox_user, status = data
            except:
                try:
                    user_db, item, status = data
                except:
                    pass

        # =====================
        # 📢 MESSAGE + STATUS VIEW
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

        except Exception as e:
            print("[TICKET] send error:", e)

        return channel
