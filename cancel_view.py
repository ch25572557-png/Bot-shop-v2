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
                f"✅ เติมสต๊อก {self.item} +{qty}",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ error: {e}",
                ephemeral=True
            )


# =====================
# 📦 STOCK SELECT (SAFE + FUTURE READY)
# =====================
class StockSelect(discord.ui.Select):

    def __init__(self, bot):
        self.bot = bot

        items = []

        try:
            cur = bot.mem.conn.cursor()
            cur.execute("SELECT name FROM stock")
            items = cur.fetchall()
        except Exception as e:
            print("[STOCK LOAD ERROR]", e)
            items = []

        options = [
            discord.SelectOption(label=i[0], value=i[0])
            for i in items[:25]
        ]

        # fallback
        if not options:
            options = [
                discord.SelectOption(
                    label="ไม่มีสินค้าในสต๊อก",
                    value="none"
                )
            ]

        super().__init__(
            placeholder="📦 เลือกสินค้าที่ต้องการเติม",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        value = self.values[0]

        if value == "none":
            return await interaction.response.send_message(
                "❌ ไม่มีสินค้าในสต๊อก",
                ephemeral=True
            )

        await interaction.response.send_modal(
            RestockModal(self.bot, value)
        )


# =====================
# 📦 MAIN VIEW
# =====================
class StockView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(StockSelect(bot))
