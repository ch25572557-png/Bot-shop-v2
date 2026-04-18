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

        try:
            await interaction.response.send_modal(OrderModal(self.bot))
        except Exception as e:
            print("[SHOP] modal error:", e)


# =====================
# 🧾 ORDER MODAL
# =====================
class OrderModal(discord.ui.Modal, title="🛒 สั่งสินค้า"):

    item = discord.ui.TextInput(label="ชื่อสินค้า", required=True)
    amount = discord.ui.TextInput(label="จำนวน", default="1", required=True)
    roblox_user = discord.ui.TextInput(label="Username Roblox", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        # =====================
        # 🔒 SAFE ITEM
        # =====================
        item = self.item.value.strip()

        if not item:
            await interaction.response.send_message(
                "❌ กรุณาใส่ชื่อสินค้า",
                ephemeral=True
            )
            return

        # =====================
        # 🔢 SAFE AMOUNT
        # =====================
        try:
            amount = int(self.amount.value)
            if amount <= 0:
                amount = 1
        except:
            amount = 1

        # =====================
        # 🎮 ROBLOX USER SAFE
        # =====================
        roblox_user = None

        try:
            roblox_user = self.roblox_user.value.strip()
            if roblox_user == "":
                roblox_user = None
        except:
            roblox_user = None

        # =====================
        # 🟢 CREATE ORDER
        # =====================
        try:
            await self.bot.order.create(
                interaction.guild,
                interaction.user,
                item,
                amount,
                roblox_user
            )

        except Exception as e:
            print("[SHOP] order create error:", e)

            await interaction.response.send_message(
                "❌ สร้างออเดอร์ไม่สำเร็จ",
                ephemeral=True
            )
            return

        # =====================
        # 📢 SUCCESS MESSAGE
        # =====================
        try:
            await interaction.response.send_message(
                "✅ สั่งซื้อสำเร็จ\n🎫 กำลังเปิด Ticket...",
                ephemeral=True
            )
        except Exception as e:
            print("[SHOP] response error:", e)
