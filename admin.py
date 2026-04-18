import discord

class AdminView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    # =====================
    # ➕ ADD PRODUCT
    # =====================
    @discord.ui.button(label="➕ เพิ่มสินค้า", style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddModal(self.bot))

    # =====================
    # 📋 VIEW ORDERS
    # =====================
    @discord.ui.button(label="📋 ดูออเดอร์", style=discord.ButtonStyle.blurple)
    async def view_orders(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            orders = self.bot.mem.get_all_orders()
        except:
            orders = []

        if not orders:
            await interaction.response.send_message("❌ ไม่มีออเดอร์", ephemeral=True)
            return

        # 📦 แสดงสูงสุด 10 ออเดอร์
        msg = "📋 ORDER LIST\n\n"

        for order in orders[:10]:
            order_id, user, item, status = order
            msg += f"🆔 {order_id} | 👤 {user} | 📦 {item} | 🔄 {status}\n"

        await interaction.response.send_message(msg, ephemeral=True)


# =====================
# 🧾 ADD PRODUCT MODAL
# =====================

class AddModal(discord.ui.Modal, title="Add Product"):

    name = discord.ui.TextInput(label="ชื่อ")
    price = discord.ui.TextInput(label="ราคา")
    stock = discord.ui.TextInput(label="จำนวน")

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        # 🛡 กัน input พัง
        try:
            name = self.name.value.strip()
            price = float(self.price.value)
            qty = int(self.stock.value)
        except:
            await interaction.response.send_message(
                "❌ ข้อมูลไม่ถูกต้อง",
                ephemeral=True
            )
            return

        # 📦 เพิ่มสินค้า
        try:
            self.bot.stock.add(name, qty, price)
        except:
            await interaction.response.send_message(
                "❌ เพิ่มสินค้าไม่สำเร็จ",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"✅ เพิ่มสินค้าแล้ว\n📦 {name} | {qty} ชิ้น | {price} บาท",
            ephemeral=True
        )
