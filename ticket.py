import discord
from status_view import StatusView

class TicketSystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 📢 SEND TO ADMIN CHANNEL (NEW)
    # =====================
    async def send_to_admin(self, guild, message: str):
        try:
            ch_id = self.brain.get("ORDER_NOTIFY")  # 👈 ใช้ config ที่คุณตั้งไว้

            if not ch_id:
                return

            channel = guild.get_channel(int(ch_id))

            if channel:
                await channel.send(message)

        except Exception as e:
            print("[ADMIN NOTIFY ERROR]", e)

    # =====================
    # 🎫 CREATE TICKET
    # =====================
    async def create(self, guild, user, order_id):

        # =====================
        # 📁 CATEGORY RESOLVE
        # =====================
        category = None

        try:
            category_id = self.brain.get("CHANNELS.TICKET_CATEGORY")

            if category_id:
                category_id = int(category_id)

                ch = guild.get_channel(category_id)

                if isinstance(ch, discord.CategoryChannel):
                    category = ch
                else:
                    category = await guild.fetch_channel(category_id)

                    if not isinstance(category, discord.CategoryChannel):
                        category = None

        except Exception as e:
            print("[TICKET] category error:", e)

        # =====================
        # 🔒 PERMISSIONS
        # =====================
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
        except Exception as e:
            print("[TICKET] permission error:", e)
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
        except Exception as e:
            print("[TICKET] create error:", e)
            return None

        # =====================
        # 💾 SAVE TICKET
        # =====================
        try:
            self.bot.mem.save_ticket(order_id, str(channel.id))
        except Exception as e:
            print("[TICKET] save error:", e)

        # =====================
        # 📦 ORDER DATA
        # =====================
        item = "Unknown"
        amount = 1
        roblox_user = None

        try:
            data = self.bot.mem.get_order(order_id)

            if data:
                data = list(data) + [None]*5
                user_db, item, amount, roblox_user, status = data[:5]

        except Exception as e:
            print("[TICKET] order load error:", e)

        # =====================
        # 📢 SEND TO ADMIN (🔥 FIX สำคัญ)
        # =====================
        try:
            await self.send_to_admin(
                guild,
                f"🆕 ORDER #{order_id}\n"
                f"👤 {user}\n"
                f"📦 {item} x{amount}"
            )
        except:
            pass

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

        except Exception as e:
            print("[TICKET] send error:", e)

        return channel
