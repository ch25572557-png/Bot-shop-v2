import discord
from permissions import admin_only


# =====================
# 📦 MODAL (+/- AMOUNT)
# =====================
class StockAmountModal(discord.ui.Modal):

    def __init__(self, bot, item, mode):
        super().__init__(title=f"{'➕ เพิ่ม' if mode=='add' else '➖ ลด'} Stock")
        self.bot = bot
        self.item = item
        self.mode = mode

        self.amount = discord.ui.TextInput(
            label="จำนวน",
            placeholder="เช่น 10",
            required=True
        )

        self.add_item(self.amount)

    async def on_submit(self, interaction: discord.Interaction):

        try:
            qty = int(self.amount.value)

            if qty <= 0:
                return await interaction.response.send_message(
                    "❌ จำนวนไม่ถูกต้อง",
                    ephemeral=True
                )

            # =====================
            # ➕ ADD STOCK
            # =====================
            if self.mode == "add":

                await self.bot.mem.add_stock(self.item, qty)

                msg = f"✅ เพิ่ม {self.item} +{qty}"

            # =====================
            # ➖ REMOVE STOCK
            # =====================
            else:

                success = await self.bot.mem.minus_stock(self.item, qty)

                if not success:
                    return await interaction.response.send_message(
                        "❌ สต๊อกไม่พอ",
                        ephemeral=True
                    )

                msg = f"⚠️ ลด {self.item} -{qty}"

            await interaction.response.send_message(msg, ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ ERROR: {e}",
                ephemeral=True
            )


# =====================
# 📦 STOCK CONTROL VIEW
# =====================
class StockControlView(discord.ui.View):

    def __init__(self, bot, item):
        super().__init__(timeout=None)
        self.bot = bot
        self.item = item

    async def interaction_check(self, interaction: discord.Interaction):
        return await admin_only(interaction)

    # ➕ เพิ่ม
    @discord.ui.button(label="➕ เพิ่ม", style=discord.ButtonStyle.green)
    async def add_stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            await interaction.response.send_modal(
                StockAmountModal(self.bot, self.item, "add")
            )
        except Exception as e:
            print("[MODAL ERROR ADD]", e)

    # ➖ ลด
    @discord.ui.button(label="➖ ลด", style=discord.ButtonStyle.red)
    async def remove_stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            await interaction.response.send_modal(
                StockAmountModal(self.bot, self.item, "remove")
            )
        except Exception as e:
            print("[MODAL ERROR REMOVE]", e)
