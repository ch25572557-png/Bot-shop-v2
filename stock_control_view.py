import discord

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

            cur = self.bot.mem.conn.cursor()

            if self.mode == "add":
                cur.execute(
                    "UPDATE stock SET qty = qty + ? WHERE name=?",
                    (qty, self.item)
                )
                msg = f"✅ เพิ่ม {self.item} +{qty}"

            else:
                cur.execute(
                    "UPDATE stock SET qty = qty - ? WHERE name=? AND qty >= ?",
                    (qty, self.item, qty)
                )
                msg = f"⚠️ ลด {self.item} -{qty}"

            self.bot.mem.conn.commit()

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
        super().__init__(timeout=60)
        self.bot = bot
        self.item = item

    # ➕ เพิ่ม (เปิด modal)
    @discord.ui.button(label="➕ เพิ่ม", style=discord.ButtonStyle.green)
    async def add_stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(
            StockAmountModal(self.bot, self.item, "add")
        )

    # ➖ ลด (เปิด modal)
    @discord.ui.button(label="➖ ลด", style=discord.ButtonStyle.red)
    async def remove_stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(
            StockAmountModal(self.bot, self.item, "remove")
        )
