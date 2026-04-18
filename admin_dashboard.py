import discord

# =====================
# 📊 VIEW STOCK
# =====================
class ViewStock(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot

    @discord.ui.button(label="📦 ดูสต๊อก", style=discord.ButtonStyle.green)
    async def stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        cur = self.bot.mem.conn.cursor()
        cur.execute("SELECT name, qty FROM stock")
        data = cur.fetchall()

        msg = "📦 STOCK LIST\n\n"

        for name, qty in data:
            msg += f"• {name} = {qty}\n"

        await interaction.response.send_message(msg, ephemeral=True)


# =====================
# 📊 VIEW ORDERS
# =====================
class ViewOrders(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot

    @discord.ui.button(label="📊 ดูออเดอร์", style=discord.ButtonStyle.blurple)
    async def orders(self, interaction: discord.Interaction, button: discord.ui.Button):

        cur = self.bot.mem.conn.cursor()
        cur.execute("SELECT id, item, amount, status FROM orders ORDER BY id DESC LIMIT 10")
        data = cur.fetchall()

        msg = "📊 RECENT ORDERS\n\n"

        for o in data:
            msg += f"#{o[0]} | {o[1]} x{o[2]} | {o[3]}\n"

        await interaction.response.send_message(msg, ephemeral=True)


# =====================
# 🧠 MAIN DASHBOARD
# =====================
class AdminDashboard(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

        self.add_item(ViewStock(bot))
        self.add_item(ViewOrders(bot))
