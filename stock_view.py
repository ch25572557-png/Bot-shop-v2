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

            # =====================
            # 🔥 MEMORY V2 ONLY
            # =====================
            await self.bot.mem.add_stock(self.item, qty)

            await interaction.response.send_message(
                f"✅ เติมสต๊อก: {self.item} +{qty}",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ error: {e}",
                ephemeral=True
            )


# =====================
# 📦 SELECT ITEM (V2 FIXED)
# =====================
class StockSelect(discord.ui.Select):

    def __init__(self, bot):
        self.bot = bot

        options = []

        # =====================
        # 🔥 MEMORY V2 FETCH
        # =====================
        try:
            # ต้องเพิ่มฟังก์ชันนี้ใน Memory V2:
            # async def get_all_stock(self)
            items = asyncio.run(self._get_items_safe())
        except:
            items = []

        for name in items[:25]:
            options.append(
                discord.SelectOption(label=name, value=name)
            )

        if not options:
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

    async def _get_items_safe(self):
        data = await self.bot.mem.get_all_stock()
        return [i[0] for i in data]

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
# 📦 VIEW (PERSISTENT)
# =====================
class StockView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(StockSelect(bot))
