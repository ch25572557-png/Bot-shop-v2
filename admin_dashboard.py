import discord

# =====================
# 📦 STOCK VIEW
# =====================
class StockButton(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)  # 🔥 FIX: ไม่ timeout
        self.bot = bot

    @discord.ui.button(
        label="📦 ดูสต๊อก",
        style=discord.ButtonStyle.green,
        custom_id="dashboard_stock_view"
    )
    async def stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            cur = self.bot.mem.conn.cursor()
            cur.execute("SELECT name, qty FROM stock")
            data = cur.fetchall()

            if not data:
                return await interaction.response.send_message(
                    "❌ ไม่มีสต๊อก",
                    ephemeral=True
                )

            msg = "📦 STOCK LIST\n\n"

            for name, qty in data[:20]:
                msg += f"• {name} = {qty}\n"

        except Exception as e:
            msg = f"❌ ERROR STOCK: {e}"

        await interaction.response.send_message(msg, ephemeral=True)


# =====================
# 📊 ORDERS VIEW
# =====================
class OrdersButton(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)  # 🔥 FIX
        self.bot = bot

    @discord.ui.button(
        label="📊 ดูออเดอร์",
        style=discord.ButtonStyle.blurple,
        custom_id="dashboard_orders_view"
    )
    async def orders(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            cur = self.bot.mem.conn.cursor()
            cur.execute(
                "SELECT id, item, amount, status FROM orders ORDER BY id DESC LIMIT 10"
            )
            data = cur.fetchall()

            if not data:
                return await interaction.response.send_message(
                    "❌ ไม่มีออเดอร์",
                    ephemeral=True
                )

            msg = "📊 RECENT ORDERS\n\n"

            for o in data:
                msg += f"#{o[0]} | {o[1]} x{o[2]} | {o[3]}\n"

        except Exception as e:
            msg = f"❌ ERROR ORDERS: {e}"

        await interaction.response.send_message(msg, ephemeral=True)


# =====================
# 🧠 MAIN DASHBOARD
# =====================
class AdminDashboard(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)  # 🔥 สำคัญมาก
        self.bot = bot

    def is_admin(self, interaction):
        try:
            role_id = self.bot.brain.role("ADMIN_ROLE")
            return any(r.id == int(role_id) for r in interaction.user.roles)
        except:
            return False

    @discord.ui.button(
        label="📦 STOCK",
        style=discord.ButtonStyle.green,
        custom_id="dashboard_open_stock"
    )
    async def open_stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        await interaction.response.send_message(
            content="📦 เมนูสต๊อก",
            view=StockButton(self.bot),
            ephemeral=True
        )

    @discord.ui.button(
        label="📊 ORDERS",
        style=discord.ButtonStyle.blurple,
        custom_id="dashboard_open_orders"
    )
    async def open_orders(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        await interaction.response.send_message(
            content="📊 เมนูออเดอร์",
            view=OrdersButton(self.bot),
            ephemeral=True
        )
