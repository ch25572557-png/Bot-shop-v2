import discord

class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_id = order_id

    # =====================
    # ⏳ WAIT ADMIN
    # =====================
    @discord.ui.button(label="⏳ รอแอดมินรับออเดอร์", style=discord.ButtonStyle.gray)
    async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.bot.mem.update_order_status(self.order_id, "WAIT_ADMIN")
        except:
            pass

        await interaction.response.send_message("⏳ อัปเดตเป็น WAIT_ADMIN แล้ว", ephemeral=True)

    # =====================
    # 👨‍💼 ADMIN ACCEPT
    # =====================
    @discord.ui.button(label="👨‍💼 แอดมินรับออเดอร์แล้ว", style=discord.ButtonStyle.blurple)
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.bot.mem.update_order_status(self.order_id, "ADMIN_ACCEPTED")
        except:
            pass

        await interaction.response.send_message("👨‍💼 อัปเดตแล้ว", ephemeral=True)

    # =====================
    # 🪏 FARMING
    # =====================
    @discord.ui.button(label="🪏 กำลังฟาร์ม", style=discord.ButtonStyle.green)
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.bot.mem.update_order_status(self.order_id, "FARMING")
        except:
            pass

        await interaction.response.send_message("🪏 อัปเดตแล้ว", ephemeral=True)

    # =====================
    # 📦 WAIT CUSTOMER
    # =====================
    @discord.ui.button(label="📦 รอลูกค้ามารับของ", style=discord.ButtonStyle.gray)
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.bot.mem.update_order_status(self.order_id, "WAIT_CUSTOMER")
        except:
            pass

        await interaction.response.send_message("📦 อัปเดตแล้ว", ephemeral=True)

    # =====================
    # ✅ COMPLETE ORDER (สำคัญสุด)
    # =====================
    @discord.ui.button(label="✅ ส่งของเสร็จแล้ว", style=discord.ButtonStyle.green)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 🔒 กันกดซ้ำ
        try:
            data = self.bot.mem.get_order(self.order_id)
            if data and data[2] == "DONE":
                await interaction.response.send_message("❗ ออเดอร์นี้จบไปแล้ว", ephemeral=True)
                return
        except:
            pass

        await interaction.response.send_message("🔄 กำลังจบออเดอร์...", ephemeral=True)

        # 🚀 เรียกระบบ complete
        try:
            await self.bot.order.complete(interaction.channel)
        except:
            try:
                await interaction.channel.send("❌ เกิดข้อผิดพลาดตอนจบออเดอร์")
            except:
                pass
