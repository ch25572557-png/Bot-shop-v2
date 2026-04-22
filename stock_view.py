import discord


# =====================
# 📦 RESTOCK MODAL
# =====================
class RestockModal(discord.ui.Modal):

    def __init__(self, bot, item):
        super().__init__(title="📦 เติมสต๊อก")
        self.bot = bot
        self.item = item

        self.amount = discord.ui.TextInput(
            label="จำนวนที่ต้องการเติม",
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

            # 🔥 FIX: normalize กันชื่อมั่ว
            item = self.bot.mem._norm(self.item)

            await self.bot.mem.add_stock(item, qty)

            await interaction.response.send_message(
                f"✅ เติมสต๊อก: {item} +{qty}",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ error: {e}",
                ephemeral=True
            )


# =====================
# 📦 SELECT ITEM (FIXED 100%)
# =====================
class StockSelect(discord.ui.Select):

    def __init__(self, bot, items):
        self.bot = bot

        options = []

        if items:
            for name, qty in items[:25]:
                options.append(
                    discord.SelectOption(
                        label=f"{name} ({qty})",
                        value=name
                    )
                )
        else:
            options = [
                discord.SelectOption(
                    label="ไม่มีสินค้าในสต๊อก",
                    value="none"
                )
            ]

        super().__init__(
            placeholder="📦 เลือกสินค้า",
            options=options,
            custom_id="stock_select_main",
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):

        value = self.values[0]

        if value == "none":
            return await interaction.response.send_message(
                "❌ ไม่มีสินค้า",
                ephemeral=True
            )

        await interaction.response.send_modal(
            RestockModal(self.bot, value)
        )


# =====================
# 📦 VIEW (FIXED)
# =====================
class StockView(discord.ui.View):

    def __init__(self, bot, items):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(StockSelect(bot, items))
