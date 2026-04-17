import discord

class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__()
        self.bot = bot
        self.order_id = order_id

    @discord.ui.button(label="⏳ รอแอดมินรับออเดอร์")
    async def wait_admin(self, interaction, button):
        self.bot.status.set(self.order_id, "WAIT_ADMIN")
        await interaction.response.send_message("อัปเดตแล้ว", ephemeral=True)

    @discord.ui.button(label="👨‍💼 แอดมินรับออเดอร์แล้ว")
    async def admin_accept(self, interaction, button):
        self.bot.status.set(self.order_id, "ADMIN_ACCEPTED")
        await interaction.response.send_message("อัปเดตแล้ว", ephemeral=True)

    @discord.ui.button(label="🪏 กำลังฟาร์ม")
    async def farming(self, interaction, button):
        self.bot.status.set(self.order_id, "FARMING")
        await interaction.response.send_message("อัปเดตแล้ว", ephemeral=True)

    @discord.ui.button(label="📦 รอลูกค้ามารับของ")
    async def waiting_customer(self, interaction, button):
        self.bot.status.set(self.order_id, "WAIT_CUSTOMER")
        await interaction.response.send_message("อัปเดตแล้ว", ephemeral=True)

    @discord.ui.button(label="✅ ส่งของเสร็จแล้ว")
    async def done(self, interaction, button):
        self.bot.status.set(self.order_id, "DONE")
        await interaction.response.send_message("อัปเดตแล้ว", ephemeral=True)
