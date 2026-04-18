import discord

class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_id = order_id

    # =====================
    # 🔐 ADMIN CHECK
    # =====================
    def is_admin(self, interaction: discord.Interaction):
        try:
            role_id = self.bot.brain.get("ROLES.ADMIN_ROLE")

            if not role_id:
                return interaction.user.guild_permissions.administrator

            role_id = int(role_id)

            return (
                interaction.user.guild_permissions.administrator
                or any(r.id == role_id for r in interaction.user.roles)
            )
        except:
            return interaction.user.guild_permissions.administrator

    # =====================
    # 📢 SEND EMBED STATUS
    # =====================
    async def send_ticket(self, interaction, status, color=0x3498db):

        color_map = {
            "WAIT_ADMIN": 0x95a5a6,
            "ADMIN_ACCEPTED": 0x3498db,
            "FARMING": 0x2ecc71,
            "WAIT_CUSTOMER": 0xf1c40f,
            "DONE": 0x2ecc71
        }

        embed = discord.Embed(
            title="📊 STATUS UPDATE",
            description=f"🎫 Order #{self.order_id}",
            color=color_map.get(status, color)
        )

        embed.add_field(name="🔄 Status", value=status, inline=False)

        await interaction.channel.send(embed=embed)

    # =====================
    # ⛔ BLOCK NON ADMIN
    # =====================
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not self.is_admin(interaction):
            await interaction.response.send_message(
                "❌ เฉพาะแอดมินเท่านั้น",
                ephemeral=True
            )
            return False
        return True

    # =====================
    # ⏳ WAIT ADMIN
    # =====================
    @discord.ui.button(label="⏳ รอแอดมิน", style=discord.ButtonStyle.gray)
    async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.bot.mem.update_order_status(self.order_id, "WAIT_ADMIN")
        await self.send_ticket(interaction, "WAIT_ADMIN")

        await interaction.response.send_message(
            "✅ ตั้งค่า WAIT_ADMIN แล้ว",
            ephemeral=True
        )

    # =====================
    # 👨‍💼 ACCEPT
    # =====================
    @discord.ui.button(label="👨‍💼 รับออเดอร์", style=discord.ButtonStyle.blurple)
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.bot.mem.update_order_status(self.order_id, "ADMIN_ACCEPTED")
        await self.send_ticket(interaction, "ADMIN_ACCEPTED")

        await interaction.response.send_message(
            "✅ รับออเดอร์แล้ว",
            ephemeral=True
        )

    # =====================
    # 🪏 FARMING
    # =====================
    @discord.ui.button(label="🪏 กำลังฟาร์ม", style=discord.ButtonStyle.green)
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.bot.mem.update_order_status(self.order_id, "FARMING")
        await self.send_ticket(interaction, "FARMING")

        await interaction.response.send_message(
            "🪏 เริ่มฟาร์มแล้ว",
            ephemeral=True
        )

    # =====================
    # 📦 WAIT CUSTOMER
    # =====================
    @discord.ui.button(label="📦 รอลูกค้า", style=discord.ButtonStyle.gray)
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.bot.mem.update_order_status(self.order_id, "WAIT_CUSTOMER")
        await self.send_ticket(interaction, "WAIT_CUSTOMER")

        await interaction.response.send_message(
            "📦 รอลูกค้าแล้ว",
            ephemeral=True
        )

    # =====================
    # ✅ DONE
    # =====================
    @discord.ui.button(label="✅ ส่งของเสร็จแล้ว", style=discord.ButtonStyle.red)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message(
                "❌ admin only",
                ephemeral=True
            )

        await interaction.response.send_message(
            "🔄 กำลังปิดออเดอร์...",
            ephemeral=True
        )

        try:
            await self.bot.order.complete(interaction.channel)
        except Exception as e:
            print("[STATUS COMPLETE ERROR]", e)
