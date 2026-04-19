import discord
from status_view import StatusView


class TicketSystem:

    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 📢 ADMIN SEND (SAFE)
    # =====================
    async def send_to_admin(self, guild, title, desc):

        try:
            ch_id = self.brain.channel("ORDER_NOTIFY")  # 🔥 FIX
            if not ch_id:
                return

            channel = self.bot.get_channel(ch_id) or await self.bot.fetch_channel(ch_id)

            if channel:
                embed = discord.Embed(
                    title=title,
                    description=desc,
                    color=0x00ffcc
                )
                await channel.send(embed=embed)

        except Exception as e:
            print("[ADMIN SEND ERROR]", e)

    # =====================
    # 🎫 CREATE TICKET
    # =====================
    async def create(self, guild, user, order_id):

        category = None

        # =====================
        # 📁 CATEGORY SAFE
        # =====================
        try:
            category_id = self.brain.channel("TICKET_CATEGORY")  # 🔥 FIX

            if category_id:
                ch = guild.get_channel(category_id)
                if isinstance(ch, discord.CategoryChannel):
                    category = ch
                else:
                    ch = await guild.fetch_channel(category_id)
                    if isinstance(ch, discord.CategoryChannel):
                        category = ch
        except:
            category = None

        # =====================
        # 👑 ADMIN ROLE
        # =====================
        admin_role = None
        try:
            role_id = self.brain.role("ADMIN_ROLE")  # 🔥 FIX
            if role_id:
                admin_role = guild.get_role(role_id)
        except:
            admin_role = None

        # =====================
        # 🔒 PERMISSION
        # =====================
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }

            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True)

        except:
            return None

        # =====================
        # 🧱 CREATE CHANNEL
        # =====================
        try:
            channel = await guild.create_text_channel(
                name=f"ticket-{order_id}",
                category=category,
                overwrites=overwrites
            )
        except Exception as e:
            print("[TICKET CREATE ERROR]", e)
            return None

        # =====================
        # 💾 SAVE
        # =====================
        try:
            self.bot.mem.save_ticket(order_id, str(channel.id))
        except:
            pass

        # =====================
        # 📦 ORDER DATA
        # =====================
        item = "Unknown"
        amount = 1
        roblox_user = None

        try:
            data = self.bot.mem.get_order(order_id)
            if data:
                _, item, amount, roblox_user, _ = list(data)[:5]
        except:
            pass

        # =====================
        # 📢 ADMIN
        # =====================
        await self.send_to_admin(
            guild,
            "🆕 NEW ORDER",
            f"Order #{order_id}\nUser: {user}\nItem: {item} x{amount}"
        )

        # =====================
        # 🎫 TICKET EMBED
        # =====================
        embed = discord.Embed(
            title="🎫 ORDER TICKET",
            description=f"Order #{order_id}",
            color=0x3498db
        )

        embed.add_field(name="👤 User", value=user.mention, inline=False)
        embed.add_field(name="📦 Item", value=f"{item} x{amount}", inline=False)

        if roblox_user:
            embed.add_field(name="🎮 Roblox", value=roblox_user, inline=False)

        # 🔥 FIX: สถานะเริ่มต้น
        embed.add_field(
            name="📊 Status",
            value="⏳ รอแอดมินรับออเดอร์",
            inline=False
        )

        # =====================
        # 🔘 STATUS VIEW
        # =====================
        await channel.send(
            embed=embed,
            view=StatusView(self.bot, order_id)  # ต้องมี custom_id ในไฟล์นี้ด้วย
        )

        return channel
