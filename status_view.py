import discord

class StatusView(discord.ui.View):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(label="⏳ รอแอดมินรับออเดอร์", style=discord.ButtonStyle.gray)
    async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.bot.status.set("WAIT_ADMIN")
        await interaction.response.send_message("⏳ ตั้งเป็นรอแอดมินรับออเดอร์แล้ว", ephemeral=True)

    @discord.ui.button(label="👨‍💼 แอดมินรับออเดอร์แล้ว", style=discord.ButtonStyle.blurple)
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.bot.status.set("ADMIN_ACCEPTED")
        await interaction.response.send_message("👨‍💼 แอดมินรับออเดอร์แล้ว", ephemeral=True)

    @discord.ui.button(label="🪏 กำลังฟาร์ม", style=discord.ButtonStyle.green)
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.bot.status.set("FARMING")
        await interaction.response.send_message("🪏 กำลังฟาร์ม", ephemeral=True)

    @discord.ui.button(label="📦 รอลูกค้ารับของ", style=discord.ButtonStyle.gray)
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.bot.status.set("WAIT_CUSTOMER")
        await interaction.response.send_message("📦 รอลูกค้ารับของ", ephemeral=True)

    @discord.ui.button(label="✅ ส่งของเรียบร้อย", style=discord.ButtonStyle.green)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.bot.status.set("DONE")
        await interaction.response.send_message("✅ ส่งของเรียบร้อยแล้ว", ephemeral=True)
