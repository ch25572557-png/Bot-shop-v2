import discord

class StatusView(discord.ui.View):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(label="📦 กำลังเตรียม", style=discord.ButtonStyle.blurple)
    async def preparing(self, interaction, button):
        self.bot.status.set("PREPARING")
        await interaction.response.send_message("📦 เปลี่ยนเป็นกำลังเตรียม", ephemeral=True)

    @discord.ui.button(label="🚚 กำลังส่ง", style=discord.ButtonStyle.gray)
    async def shipping(self, interaction, button):
        self.bot.status.set("SHIPPING")
        await interaction.response.send_message("🚚 กำลังส่งของ", ephemeral=True)

    @discord.ui.button(label="✅ เสร็จสิ้น", style=discord.ButtonStyle.green)
    async def done(self, interaction, button):
        self.bot.status.set("DONE")
        await interaction.response.send_message("✅ ปิดงานแล้ว", ephemeral=True)
