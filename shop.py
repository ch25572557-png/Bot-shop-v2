import discord

# =====================
# 🛒 SHOP VIEW
# =====================
class ShopView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🛒 BUY", style=discord.ButtonStyle.green)
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 👉 เปิดฟอร์มให้กรอก
        await interaction.response.send_modal(OrderModal(self.bot))


# =====================
# 🧾 MODAL (ฟอร์มสั่งของ)
# =====================
class OrderModal(discord.ui.Modal, title="🛒 สั่งสินค้า"):

    item = discord.ui.TextInput(label="ชื่อสินค้า")
    amount = discord.ui.TextInput(label="จำนวน", default="1")
    roblox_user = discord.ui.TextInput(label="Username Roblox", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        # 🔒 กันจำนวนพัง
        try:
            amount = int(self.amount.value)
            if amount <= 0:
                amount = 1
        except:
            amount = 1

        # 🟢 สร้าง order
        await self.bot.order.create(
            interaction.guild,
            interaction.user,
            self.item.value,
            amount,
            self.roblox_user.value
        )

        # 📢 แจ้งผู้ใช้
        await interaction.response.send_message(
            "✅ สั่งซื้อสำเร็จ\n🎫 ระบบกำลังเปิด Ticket...",
            ephemeral=True
        )
