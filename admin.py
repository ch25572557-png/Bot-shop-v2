import discord

class AdminView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    # =====================
    # 🔐 CHECK ADMIN ROLE
    # =====================
    def is_admin(self, interaction):
        role_id = self.bot.brain.get("ROLES.ADMIN_ROLE")

        if not role_id:
            return False

        return any(str(role.id) == str(role_id) for role in interaction.user.roles)

    # =====================
    # ➕ ADD PRODUCT
    # =====================
    @discord.ui.button(label="➕ เพิ่มสินค้า", style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        await interaction.response.send_modal(AddModal(self.bot))

    # =====================
    # 📋 VIEW ORDERS
    # =====================
    @discord.ui.button(label="📋 ดูออเดอร์", style=discord.ButtonStyle.blurple)
    async def view_orders(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        orders = self.bot.mem.get_all_orders() or []
        orders = [o for o in orders if o and o[-1] != "DONE"]

        if not orders:
            return await interaction.response.send_message("❌ ไม่มีออเดอร์", ephemeral=True)

        msg = "📋 ORDERS\n\n"

        for o in orders[:10]:
            try:
                o = list(o)
                msg += f"🆔 {o[0]} | {o[1]} | {o[2]} x{o[3]} | {o[5]}\n"
            except:
                continue

        await interaction.response.send_message(msg, ephemeral=True)

    # =====================
    # ❌ CANCEL + REFUND STOCK
    # =====================
    @discord.ui.button(label="❌ ยกเลิกออเดอร์", style=discord.ButtonStyle.red)
    async def cancel_order(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        await interaction.response.send_message("🧾 ใส่ Order ID", ephemeral=True)

        def check(m):
            return m.author.id == interaction.user.id

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30)
            order_id = int(msg.content)

            order = self.bot.mem.get_order(order_id)

            if not order:
                return await interaction.followup.send("❌ ไม่พบออเดอร์", ephemeral=True)

            user, item, amount, roblox_user, status = order

            # 🔴 refund stock
            self.bot.mem.add_stock(item, amount)

            # cancel order
            self.bot.mem.update_order_status(order_id, "CANCELLED")

            await interaction.followup.send("✅ ยกเลิก + คืนสต๊อกแล้ว", ephemeral=True)

        except:
            await interaction.followup.send("❌ error / timeout", ephemeral=True)

    # =====================
    # 🔄 RESTOCK
    # =====================
    @discord.ui.button(label="🔄 รีสต็อก", style=discord.ButtonStyle.green)
    async def restock(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        await interaction.response.send_message("📦 ใส่: ชื่อ | จำนวน", ephemeral=True)

        def check(m):
            return m.author.id == interaction.user.id

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30)
            name, qty = msg.content.split("|")

            name = name.strip()
            qty = int(qty.strip())

            self.bot.stock.add(name, qty, 0)

            await interaction.followup.send("✅ รีสต็อกแล้ว", ephemeral=True)

        except:
            await interaction.followup.send("❌ format ผิด", ephemeral=True)

    # =====================
    # 📊 VIEW STOCK
    # =====================
    @discord.ui.button(label="📊 ดูสต๊อก", style=discord.ButtonStyle.gray)
    async def view_stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        cur = self.bot.mem.conn.cursor()
        cur.execute("SELECT name, qty, price FROM stock")
        data = cur.fetchall()

        if not data:
            return await interaction.response.send_message("❌ ไม่มีสต๊อก", ephemeral=True)

        msg = "📦 STOCK\n\n"

        for name, qty, price in data[:15]:
            msg += f"📦 {name} | {qty} | {price}\n"

        await interaction.response.send_message(msg, ephemeral=True)


# =====================
# 🧾 MODAL (unchanged)
# =====================
class AddModal(discord.ui.Modal, title="Add Product"):

    name = discord.ui.TextInput(label="ชื่อสินค้า", required=True)
    price = discord.ui.TextInput(label="ราคา", required=True)
    stock = discord.ui.TextInput(label="จำนวน", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        try:
            name = self.name.value.strip()
            price = float(self.price.value)
            qty = int(self.stock.value)
        except:
            return await interaction.response.send_message("❌ invalid", ephemeral=True)

        self.bot.stock.add(name, qty, price)

        await interaction.response.send_message(
            f"✅ เพิ่ม {name}",
            ephemeral=True
        )
