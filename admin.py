import discord

class AdminView(discord.ui.View):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(label="➕ เพิ่มสินค้า", style=discord.ButtonStyle.green)
    async def add(self, interaction, button):
        await interaction.response.send_modal(AddModal(self.bot))


class AddModal(discord.ui.Modal, title="Add Product"):

    name = discord.ui.TextInput(label="ชื่อ")
    price = discord.ui.TextInput(label="ราคา")
    stock = discord.ui.TextInput(label="จำนวน")

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction):

        self.bot.stock.add(
            self.name.value,
            int(self.stock.value),
            float(self.price.value)
        )

        await interaction.response.send_message(
            "✅ เพิ่มสินค้าแล้ว",
            ephemeral=True
        )
