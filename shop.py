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
# 🧾 ORDER MODAL (FIXED)
# =====================
class OrderModal(discord.ui.Modal, title="🛒 สั่งสินค้า"):

    item = discord.ui.TextInput(label="ชื่อสินค้า", required=True, max_length=100)
    amount = discord.ui.TextInput(label="จำนวน (default 1)", required=True, max_length=5)
    roblox_user = discord.ui.TextInput(label="Username Roblox", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self._locked = False  # 🔒 กันกดซ้ำ

    async def on_submit(self, interaction: discord.Interaction):

        # =====================
        # 🔒 DOUBLE SUBMIT GUARD
        # =====================
        if self._locked:
            return

        self._locked = True

        try:
            # =====================
            # 🔒 ITEM SAFE
            # =====================
            item = self.item.value.strip()

            if not item:
                await interaction.response.send_message(
                    "❌ กรุณาใส่ชื่อสินค้า",
                    ephemeral=True
                )
                return

            # =====================
            # 🔢 AMOUNT SAFE (NO CRASH)
            # =====================
            try:
                amount = int(self.amount.value)
                if amount <= 0:
                    amount = 1
            except:
                amount = 1

            # =====================
            # 🎮 ROBLOX SAFE
            # =====================
            roblox_user = None
            try:
                roblox_user = self.roblox_user.value.strip() or None
            except:
                roblox_user = None

            # =====================
            # 🟢 CREATE ORDER
            # =====================
            await self.bot.order.create(
                interaction.guild,
                interaction.user,
                item,
                amount,
                roblox_user
            )

            # =====================
            # 📢 SUCCESS
            # =====================
            await interaction.response.send_message(
                "✅ สั่งซื้อสำเร็จ\n🎫 กำลังเปิด Ticket...",
                ephemeral=True
            )

        except Exception as e:
            print("[SHOP] modal crash:", e)

            try:
                await interaction.response.send_message(
                    "❌ ระบบ error กรุณาลองใหม่",
                    ephemeral=True
                )
            except:
                pass

        finally:
            self._locked = False
