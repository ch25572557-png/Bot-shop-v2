import discord
from status_view import StatusView

class TicketSystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 📢 ADMIN SEND (EMBED FIX)
    # =====================
    async def send_to_admin(self, guild, title, desc):
        try:
            ch_id = self.brain.get("CHANNELS.ORDER_NOTIFY")
            if not ch_id:
                return

            channel = self.bot.get_channel(int(ch_id)) or await self.bot.fetch_channel(int(ch_id))

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
            category_id = self.brain.get("CHANNELS.TICKET_CATEGORY")

            if category_id:
                ch = guild.get_channel(int(category_id))
                if isinstance(ch, discord.CategoryChannel):
                    category = ch
                else:
                    ch = await guild.fetch_channel(int(category_id))
                    if isinstance(ch, discord.CategoryChannel):
                        category = ch
        except:
            category = None

        # =====================
        # 🔒 PERMISSION
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
        # 📢 ADMIN EMBED (FIX)
        # =====================
        await self.send_to_admin(
            guild,
            "🆕 NEW ORDER",
            f"Order ID: #{order_id}\nUser: {user}\nItem: {item} x{amount}"
        )

        # =====================
        # 🎫 TICKET EMBED (FIX)
        # =====================
        embed = discord.Embed(
            title="🎫 TICKET CREATED",
            description=f"Order #{order_id}",
            color=0x3498db
        )

        embed.add_field(name="👤 User", value=user.mention, inline=False)
        embed.add_field(name="📦 Item", value=f"{item} x{amount}", inline=False)

        if roblox_user:
            embed.add_field(name="🎮 Roblox", value=roblox_user, inline=False)

        embed.add_field(
            name="⚙️ Status",
            value="ใช้ปุ่มด้านล่างเพื่อจัดการออเดอร์",
            inline=False
        )

        # =====================
        # 🔘 STATUS VIEW
        # =====================
        await channel.send(embed=embed, view=StatusView(self.bot, order_id))

        return channel
