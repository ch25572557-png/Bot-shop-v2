import discord

class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_id = order_id

    # =====================
    # 🔐 ADMIN CHECK (FIX)
    # =====================
    def is_admin(self, interaction: discord.Interaction):
        try:
            role_id = self.bot.brain.role("ADMIN_ROLE")  # 🔥 FIX

            if not role_id:
                return interaction.user.guild_permissions.administrator

            return (
                interaction.user.guild_permissions.administrator
                or any(r.id == role_id for r in interaction.user.roles)
            )
        except:
            return interaction.user.guild_permissions.administrator

    # =====================
    # 📢 STATUS EMBED
    # =====================
    async def send_ticket(self, interaction, status):

        color_map = {
            "WAIT_ADMIN": 0x95a5a6,
            "ADMIN_ACCEPTED": 0x3498db,
            "FARMING": 0x2ecc71,
            "WAIT_CUSTOMER": 0xf1c40f,
            "DONE": 0x2ecc71
        }

        embed = discord.Embed(
            title="📊 STATUS UPDATE",
            description=f"Order #{self.order_id}",
            color=color_map.get(status, 0x3498db)
        )

        embed.add_field(name="🔄 Status", value=status, inline=False)

        await interaction.channel.send(embed=embed)

    # =====================
    # ⛔ BLOCK NON ADMIN
    # =====================
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not self.is_admin(interaction):
            await interaction.response.send_message(
                "❌ เฉพาะแอดมิน",
                ephemeral=True
            )
            return False
        return True

    # =====================
    # ⏳ WAIT ADMIN
    # =====================
    @discord.ui.button(
        label="⏳ รอแอดมิน",
        style=discord.ButtonStyle.gray,
        custom_id="status_wait_admin"
    )
    async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        self.bot.mem.update_order_status(self.order_id, "WAIT_ADMIN")
        await self.send_ticket(interaction, "WAIT_ADMIN")

        await interaction.followup.send("✅ WAIT_ADMIN", ephemeral=True)

    # =====================
    # 👨‍💼 ACCEPT
    # =====================
    @discord.ui.button(
        label="👨‍💼 รับออเดอร์",
        style=discord.ButtonStyle.blurple,
        custom_id="status_accept"
    )
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        self.bot.mem.update_order_status(self.order_id, "ADMIN_ACCEPTED")
        await self.send_ticket(interaction, "ADMIN_ACCEPTED")

        await interaction.followup.send("✅ รับออเดอร์แล้ว", ephemeral=True)

    # =====================
    # 🪏 FARMING
    # =====================
    @discord.ui.button(
        label="🪏 กำลังฟาร์ม",
        style=discord.ButtonStyle.green,
        custom_id="status_farming"
    )
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        self.bot.mem.update_order_status(self.order_id, "FARMING")
        await self.send_ticket(interaction, "FARMING")

        await interaction.followup.send("🪏 ฟาร์มแล้ว", ephemeral=True)

    # =====================
    # 📦 WAIT CUSTOMER
    # =====================
    @discord.ui.button(
        label="📦 รอลูกค้า",
        style=discord.ButtonStyle.gray,
        custom_id="status_wait_customer"
    )
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        self.bot.mem.update_order_status(self.order_id, "WAIT_CUSTOMER")
        await self.send_ticket(interaction, "WAIT_CUSTOMER")

        await interaction.followup.send("📦 รอลูกค้า", ephemeral=True)

    # =====================
    # ✅ DONE (🔥 FIX สำคัญสุด)
    # =====================
    @discord.ui.button(
        label="✅ ส่งของเสร็จแล้ว",
        style=discord.ButtonStyle.red,
        custom_id="status_done"
    )
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        try:
            # 🔥 update ก่อน
            self.bot.mem.update_order_status(self.order_id, "DONE")

            success = await self.bot.order.complete(interaction.channel)

            if success:
                await interaction.followup.send("✅ ปิดออเดอร์แล้ว", ephemeral=True)
            else:
                await interaction.followup.send("❌ ปิดไม่สำเร็จ", ephemeral=True)

        except Exception as e:
            print("[STATUS COMPLETE ERROR]", e)
            await interaction.followup.send("❌ ERROR", ephemeral=True)
