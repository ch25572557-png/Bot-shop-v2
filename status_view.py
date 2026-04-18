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
        except Exception as e:
            print(e)

        await interaction.response.send_message("⏳ อัปเดต WAIT_ADMIN แล้ว", ephemeral=True)

    # =====================
    # 👨‍💼 ADMIN ACCEPT
    # =====================
    @discord.ui.button(label="👨‍💼 แอดมินรับออเดอร์แล้ว", style=discord.ButtonStyle.blurple)
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            self.bot.mem.update_order_status(self.order_id, "ADMIN_ACCEPTED")
        except Exception as e:
            print(e)

        await interaction.response.send_message("👨‍💼 อัปเดตแล้ว", ephemeral=True)

    # =====================
    # 🪏 FARMING
    # =====================
    @discord.ui.button(label="🪏 กำลังฟาร์ม", style=discord.ButtonStyle.green)
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            self.bot.mem.update_order_status(self.order_id, "FARMING")
        except Exception as e:
            print(e)

        await interaction.response.send_message("🪏 อัปเดตแล้ว", ephemeral=True)

    # =====================
    # 📦 WAIT CUSTOMER
    # =====================
    @discord.ui.button(label="📦 รอลูกค้ามารับของ", style=discord.ButtonStyle.gray)
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            self.bot.mem.update_order_status(self.order_id, "WAIT_CUSTOMER")
        except Exception as e:
            print(e)

        await interaction.response.send_message("📦 อัปเดตแล้ว", ephemeral=True)

    # =====================
    # ✅ DONE (CORE FLOW)
    # =====================
    @discord.ui.button(label="✅ ส่งของเสร็จแล้ว", style=discord.ButtonStyle.green)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 🔒 กันกดซ้ำ (ปลอดภัยขึ้น)
        try:
            data = self.bot.mem.get_order(self.order_id)
            if not data:
                await interaction.response.send_message("❌ ไม่พบออเดอร์", ephemeral=True)
                return

            if data[4] == "DONE":
                await interaction.response.send_message("❗ ออเดอร์นี้จบแล้ว", ephemeral=True)
                return
        except Exception as e:
            print(e)

        await interaction.response.send_message("🔄 กำลังจบออเดอร์...", ephemeral=True)

        # 🚀 เรียกระบบหลัก (order system)
        try:
            await self.bot.order.complete(interaction.channel)
        except Exception as e:
            print(e)
            try:
                await interaction.channel.send("❌ error ตอน complete order")
            except:
                pass
