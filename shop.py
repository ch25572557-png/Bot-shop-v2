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
        custom_id="shop_buy_button"
    )
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(OrderModal(self.bot))


# =====================
# 🧾 ORDER MODAL (FIXED)
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
            # =====================
            # 📦 NORMALIZE ITEM
            # =====================
            item = self.item.value.strip().lower()

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
            # 🔍 STOCK FIX (🔥 สำคัญมาก)
            # =====================
            stock = await self.bot.mem.get_stock(item)

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
            # 🎮 ROBLOX USER
            # =====================
            roblox_user = self.roblox_user.value.strip() or None

            # =====================
            # 🛒 CREATE ORDER (FIXED CALL)
            # =====================
            order_id = await self.bot.mem.add_order(
                interaction.user.name,
                item,
                amount,
                roblox_user,
                "PENDING"
            )

            if not order_id:
                return await interaction.response.send_message(
                    "❌ สร้างออเดอร์ไม่สำเร็จ",
                    ephemeral=True
                )

            # =====================
            # 🎫 CREATE TICKET (IMPORTANT FIX)
            # =====================
            await self.bot.ticket.create(
                interaction.guild,
                interaction.user,
                order_id,
                interaction
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
