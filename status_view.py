import discord

class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_id = order_id
        self.locked = False

    # =====================
    # 🔐 ADMIN CHECK (ROBUST)
    # =====================
    def is_admin(self, interaction: discord.Interaction):

        role_id = self.bot.brain.get("ROLES.ADMIN_ROLE")

        if role_id:
            role = interaction.guild.get_role(int(role_id))
            if role in interaction.user.roles:
                return True

        return interaction.user.guild_permissions.administrator

    # =====================
    # ⛔ GLOBAL BLOCK
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
    # ✅ DONE (SAFE FINAL)
    # =====================
    @discord.ui.button(label="✅ ส่งของเสร็จแล้ว", style=discord.ButtonStyle.red)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 🔐 admin check (double safety)
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ admin only", ephemeral=True)
            return

        # 🧠 กันกดซ้ำ
        if self.locked:
            await interaction.response.send_message("❌ กำลังดำเนินการอยู่", ephemeral=True)
            return

        self.locked = True

        try:
            await interaction.response.send_message("🔄 กำลังจบออเดอร์...", ephemeral=True)

            await self.bot.order.complete(interaction.channel)

        except Exception as e:
            print("[STATUS] complete error:", e)

        finally:
            self.locked = False
