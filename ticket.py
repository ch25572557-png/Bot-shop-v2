import discord
from status_view import StatusView


class TicketSystem:

    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 📢 ADMIN SEND
    # =====================
    async def send_to_admin(self, guild, title, desc):

        try:
            ch_id = self.brain.channel("ORDER_NOTIFY")
            if not ch_id:
                return

            ch_id = int(ch_id)

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
    # 🎫 CREATE TICKET (FIXED)
    # =====================
    async def create(self, guild, user, order_id, interaction=None):

        category = None

        # =====================
        # 📁 CATEGORY FIX
        # =====================
        try:
            category_id = self.brain.channel("TICKET_CATEGORY")

            if category_id:
                category_id = int(category_id)
                ch = self.bot.get_channel(category_id) or await self.bot.fetch_channel(category_id)

                if isinstance(ch, discord.CategoryChannel):
                    category = ch

        except Exception as e:
            print("[CATEGORY ERROR]", e)

        # =====================
        # 👑 ADMIN ROLE FIX
        # =====================
        admin_role = None

        try:
            role_id = self.brain.role("ADMIN_ROLE")
            if role_id:
                admin_role = guild.get_role(int(role_id))
        except:
            pass

        # =====================
        # 🔒 PERMISSIONS FIX
        # =====================
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True)

        # =====================
        # 🧱 CREATE CHANNEL SAFE
        # =====================
        try:
            channel = await guild.create_text_channel(
                name=f"ticket-{order_id}",
                category=category,
                overwrites=overwrites
            )
        except Exception as e:
            print("[TICKET CREATE ERROR]", e)

            # 🔥 FIX: ตอบ interaction กัน "ปุ่มเหมือนไม่ทำงาน"
            if interaction:
                await interaction.response.send_message("❌ สร้างทิกเก็ตไม่สำเร็จ", ephemeral=True)

            return None

        # =====================
        # 💾 SAVE
        # =====================
        try:
            await self.bot.mem.save_ticket(order_id, str(channel.id))
        except:
            pass

        # =====================
        # 📦 ORDER DATA
        # =====================
        item = "Unknown"
        amount = 1
        roblox_user = None

        try:
            data = await self.bot.mem.get_order(order_id)
            if data:
                _, item, amount, roblox_user, _ = data
        except:
            pass

        # =====================
        # 📢 ADMIN NOTIFY
        # =====================
        await self.send_to_admin(
            guild,
            "🆕 NEW ORDER",
            f"Order #{order_id}\nUser: {user}\nItem: {item} x{amount}"
        )

        # =====================
        # 🎫 EMBED
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

        embed.add_field(
            name="📊 Status",
            value="⏳ รอแอดมินรับออเดอร์",
            inline=False
        )

        # =====================
        # 🔘 VIEW
        # =====================
        await channel.send(
            embed=embed,
            view=StatusView(self.bot, order_id)
        )

        return channel
