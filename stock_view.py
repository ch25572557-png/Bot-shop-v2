import discord

# =====================
# 📦 RESTOCK MODAL
# =====================
class RestockModal(discord.ui.Modal, title="📦 เติมสต๊อก"):

    amount = discord.ui.TextInput(
        label="จำนวนที่ต้องการเติม",
        placeholder="เช่น 10",
        required=True
    )

    def __init__(self, bot, item):
        super().__init__()
        self.bot = bot
        self.item = item

    async def on_submit(self, interaction: discord.Interaction):

        try:
            qty = int(self.amount.value)

            if qty <= 0:
                return await interaction.response.send_message(
                    "❌ จำนวนไม่ถูกต้อง",
                    ephemeral=True
                )

            self.bot.stock.add(self.item, qty, 0)

            await interaction.response.send_message(
                f"✅ เติมสต๊อก: {self.item} +{qty}",
                ephemeral=True
            )

        except:
            await interaction.response.send_message(
                "❌ error",
                ephemeral=True
            )


# =====================
# 📦 SELECT ITEM
# =====================
class StockSelect(discord.ui.Select):

    def __init__(self, bot):
        self.bot = bot

        cur = bot.mem.conn.cursor()
        cur.execute("SELECT name FROM stock")
        items = cur.fetchall()

        options = []

        for i in items[:25]:
            name = i[0]

            options.append(
                discord.SelectOption(
                    label=name,
                    value=name
                )
            )

        super().__init__(
            placeholder="📦 เลือกสินค้าที่ต้องการเติม",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        item = self.values[0]

        await interaction.response.send_modal(
            RestockModal(self.bot, item)
        )


# =====================
# 📦 VIEW หลัก
# =====================
class StockView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(StockSelect(bot))
