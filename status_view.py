import discord

class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_id = order_id

    # =====================
    # 🔐 CHECK ADMIN ONLY
    # =====================
    def is_admin(self, interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator

    # =====================
    # ⛔ BLOCK NON ADMIN
    # =====================
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # allow only admin for ALL buttons
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
    @discord.ui.button(label="⏳ รอแอดมินรับออเดอร์", style=discord.ButtonStyle.gray)
    async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.bot.mem.update_order_status(self.order_id, "WAIT_ADMIN")
        await interaction.response.send_message("⏳ WAIT_ADMIN", ephemeral=True)

    # =====================
    # 👨‍💼 ACCEPT
    # =====================
    @discord.ui.button(label="👨‍💼 รับออเดอร์", style=discord.ButtonStyle.blurple)
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.bot.mem.update_order_status(self.order_id, "ADMIN_ACCEPTED")
        await interaction.response.send_message("👨‍💼 ADMIN_ACCEPTED", ephemeral=True)

    # =====================
    # 🪏 FARM
    # =====================
    @discord.ui.button(label="🪏 ฟาร์ม", style=discord.ButtonStyle.green)
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.bot.mem.update_order_status(self.order_id, "FARMING")
        await interaction.response.send_message("🪏 FARMING", ephemeral=True)

    # =====================
    # 📦 WAIT CUSTOMER
    # =====================
    @discord.ui.button(label="📦 รอลูกค้า", style=discord.ButtonStyle.gray)
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.bot.mem.update_order_status(self.order_id, "WAIT_CUSTOMER")
        await interaction.response.send_message("📦 WAIT_CUSTOMER", ephemeral=True)

    # =====================
    # ❌ DONE (ADMIN ONLY)
    # =====================
    @discord.ui.button(label="✅ ส่งของเสร็จแล้ว", style=discord.ButtonStyle.red)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 🔐 admin lock (double safety)
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ admin only", ephemeral=True)
            return

        try:
            await interaction.response.send_message("🔄 กำลังจบออเดอร์...", ephemeral=True)
        except:
            pass

        try:
            await self.bot.order.complete(interaction.channel)
        except Exception as e:
            print("[STATUS] complete error:", e)
