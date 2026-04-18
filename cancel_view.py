import discord
from cancel_modal import CancelOrderModal

class CancelView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="❌ Cancel Order",
        style=discord.ButtonStyle.red
    )
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 🔐 admin only
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "❌ admin only",
                ephemeral=True
            )

        await interaction.response.send_modal(CancelOrderModal(self.bot))
