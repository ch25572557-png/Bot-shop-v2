import discord
from status_view import StatusView


class TicketSystem:

    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    async def send_to_admin(self, guild, title, desc):
        try:
            ch_id = self.brain.channel("ORDER_NOTIFY")
            if not ch_id:
                return

            channel = self.bot.get_channel(int(ch_id)) or await self.bot.fetch_channel(int(ch_id))

            if channel:
                await channel.send(embed=discord.Embed(
                    title=title,
                    description=desc,
                    color=0x00ffcc
                ))
        except Exception as e:
            print("[ADMIN SEND ERROR]", e)

    async def create(self, guild, user, order_id, interaction=None):

        # =====================
        # 📁 CATEGORY
        # =====================
        category = None
        try:
            cid = self.brain.channel("TICKET_CATEGORY")
            if cid:
                category = discord.utils.get(guild.categories, id=int(cid))
        except:
            pass

        # =====================
        # 👑 ADMIN ROLE
        # =====================
        admin_role = None
        try:
            rid = self.brain.role("ADMIN_ROLE")
            if rid:
                admin_role = guild.get_role(int(rid))
        except:
            pass

        # =====================
        # 🔒 PERMISSIONS (FINAL)
        # =====================
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),

            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
        }

        # 👤 ลูกค้า
        if isinstance(user, discord.Member):
            overwrites[user] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        # 👑 แอดมิน
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        # =====================
        # 🧱 CREATE CHANNEL
        # =====================
        try:
            channel = await guild.create_text_channel(
                name=f"order-{order_id}",
                category=category,
                overwrites=overwrites
            )
        except Exception as e:
            print("[TICKET CREATE ERROR]", e)
            return None

        await self.bot.mem.save_ticket(order_id, str(channel.id))

        # =====================
        # 📦 DATA
        # =====================
        item = "Unknown"
        amount = 1
        roblox_user = None

        data = await self.bot.mem.get_order(order_id)
        if data:
            _, item, amount, roblox_user, _ = data

        # =====================
        # 📢 ADMIN NOTIFY
        # =====================
        await self.send_to_admin(
            guild,
            "🆕 NEW ORDER",
            f"Order #{order_id}\nUser: {getattr(user,'name',user)}\nItem: {item} x{amount}"
        )

        # =====================
        # 🎫 EMBED
        # =====================
        embed = discord.Embed(
            title="🎫 ORDER TICKET",
            description=f"Order #{order_id}",
            color=0x3498db
        )

        embed.add_field(name="👤 User", value=getattr(user, "mention", str(user)), inline=False)
        embed.add_field(name="📦 Item", value=f"{item} x{amount}", inline=False)

        if roblox_user:
            embed.add_field(name="🎮 Roblox", value=roblox_user, inline=False)

        embed.add_field(name="📊 Status", value="⏳ รอแอดมินรับออเดอร์", inline=False)

        # =====================
        # 🔘 VIEW
        # =====================
        await channel.send(
            embed=embed,
            view=StatusView(self.bot, order_id)
        )

        return channel
