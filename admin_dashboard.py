import discord

# =====================
# 📦 STOCK VIEW
# =====================
class StockButton(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot

    @discord.ui.button(label="📦 ดูสต๊อก", style=discord.ButtonStyle.green)
    async def stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            cur = self.bot.mem.conn.cursor()
            cur.execute("SELECT name, qty FROM stock")
            data = cur.fetchall()

            msg = "📦 STOCK LIST\n\n"

            for name, qty in data:
                msg += f"• {name} = {qty}\n"

        except Exception as e:
            msg = f"❌ ERROR STOCK: {e}"

        await interaction.response.send_message(msg, ephemeral=True)


# =====================
# 📊 ORDERS VIEW
# =====================
class OrdersButton(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot

    @discord.ui.button(label="📊 ดูออเดอร์", style=discord.ButtonStyle.blurple)
    async def orders(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            cur = self.bot.mem.conn.cursor()
            cur.execute("SELECT id, item, amount, status FROM orders ORDER BY id DESC LIMIT 10")
            data = cur.fetchall()

            msg = "📊 RECENT ORDERS\n\n"

            for o in data:
                msg += f"#{o[0]} | {o[1]} x{o[2]} | {o[3]}\n"

        except Exception as e:
            msg = f"❌ ERROR ORDERS: {e}"

        await interaction.response.send_message(msg, ephemeral=True)


# =====================
# 🧠 MAIN DASHBOARD (FIXED + CLEAN)
# =====================
class AdminDashboard(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="📦 STOCK", style=discord.ButtonStyle.green)
    async def open_stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            content="📦 เปิดเมนูสต๊อก",
            view=StockButton(self.bot),
            ephemeral=True
        )

    @discord.ui.button(label="📊 ORDERS", style=discord.ButtonStyle.blurple)
    async def open_orders(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            content="📊 เปิดเมนูออเดอร์",
            view=OrdersButton(self.bot),
            ephemeral=True
        )
