import discord

class ShopView(discord.ui.View):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(label="🛒 BUY", style=discord.ButtonStyle.green)
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):

        await self.bot.order.create(
            interaction.guild,
            interaction.user,
            "ITEM"
        )

        await interaction.response.send_message(
            "🎫 Order Created + Ticket Opened",
            ephemeral=True
        )
