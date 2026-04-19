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

            # =====================
            # 🔥 USE MEMORY LAYER (FIX)
            # =====================
            self.bot.mem.add_stock(self.item, qty)

            # =====================
            # 📢 LOW STOCK CHECK TRIGGER
            # =====================
            try:
                low = int(self.bot.brain.setting("LOW_STOCK", 100))
                current = self.bot.mem.get_stock(self.item)

                if current > low:
                    pass  # ok
                else:
                    print(f"[LOW STOCK WARNING] {self.item} = {current}")

            except:
                pass

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
# 📦 SELECT ITEM
# =====================
class StockSelect(discord.ui.Select):

    def __init__(self, bot):
        self.bot = bot

        try:
            cur = bot.mem.conn.cursor()
            cur.execute("SELECT name FROM stock")
            items = cur.fetchall()
        except Exception as e:
            print("[STOCK SELECT ERROR]", e)
            items = []

        options = []

        for i in items[:25]:
            options.append(
                discord.SelectOption(
                    label=i[0],
                    value=i[0]
                )
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
            disabled=(len(items) == 0)
        )

    async def callback(self, interaction: discord.Interaction):

        try:
            value = self.values[0]

            if value == "none":
                return await interaction.response.send_message(
                    "❌ ไม่มีสินค้า",
                    ephemeral=True
                )

            await interaction.response.send_modal(
                RestockModal(self.bot, value)
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ error: {e}",
                ephemeral=True
            )


# =====================
# 📦 VIEW
# =====================
class StockView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(StockSelect(bot))
