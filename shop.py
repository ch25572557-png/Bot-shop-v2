import discord


# =====================
# 🛒 SHOP VIEW (FIXED)
# =====================
class ShopView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="🛒 BUY",
        style=discord.ButtonStyle.green,
        custom_id="shop_buy_button"  # 🔥 FIX สำคัญ
    )
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            await interaction.response.send_modal(OrderModal(self.bot))
        except Exception as e:
            print("[SHOP] modal error:", e)


# =====================
# 🧾 ORDER MODAL (FINAL)
# =====================
class OrderModal(discord.ui.Modal, title="🛒 สั่งสินค้า"):

    item = discord.ui.TextInput(label="ชื่อสินค้า", required=True, max_length=100)
    amount = discord.ui.TextInput(label="จำนวน (default 1)", required=True, max_length=5)
    roblox_user = discord.ui.TextInput(label="Username Roblox", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        try:
            item = self.item.value.strip()

            if not item:
                return await interaction.response.send_message(
                    "❌ กรุณาใส่ชื่อสินค้า",
                    ephemeral=True
                )

            # =====================
            # 🔢 AMOUNT SAFE
            # =====================
            try:
                amount = int(self.amount.value)
                if amount <= 0:
                    amount = 1
            except:
                amount = 1

            # =====================
            # 🔍 CHECK STOCK (🔥 ใหม่)
            # =====================
            stock = self.bot.mem.get_stock(item)

            if stock <= 0:
                return await interaction.response.send_message(
                    f"❌ สินค้า '{item}' หมด",
                    ephemeral=True
                )

            if amount > stock:
                return await interaction.response.send_message(
                    f"❌ สต๊อกมีแค่ {stock}",
                    ephemeral=True
                )

            # =====================
            # 🎮 ROBLOX
            # =====================
            roblox_user = self.roblox_user.value.strip() or None

            # =====================
            # 🛒 CREATE ORDER
            # =====================
            order_id = await self.bot.order.create(
                interaction.guild,
                interaction.user,
                item,
                amount,
                roblox_user
            )

            if not order_id:
                return await interaction.response.send_message(
                    "❌ สร้างออเดอร์ไม่สำเร็จ",
                    ephemeral=True
                )

            # =====================
            # ✅ SUCCESS
            # =====================
            await interaction.response.send_message(
                f"✅ สั่งซื้อสำเร็จ\n🆔 Order #{order_id}\n🎫 เปิด Ticket แล้ว",
                ephemeral=True
            )

        except Exception as e:
            print("[SHOP ERROR]", e)

            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ ระบบ error กรุณาลองใหม่",
                    ephemeral=True
                )
