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

        try:
            await interaction.response.send_modal(AddModal(self.bot))
        except Exception as e:
            print("[ADMIN] modal error:", e)

    # =====================
    # 📋 VIEW ORDERS (SAFE + CLEAN)
    # =====================
    @discord.ui.button(label="📋 ดูออเดอร์", style=discord.ButtonStyle.blurple)
    async def view_orders(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            orders = self.bot.mem.get_all_orders()
        except:
            orders = []

        # 🔥 filter only active
        orders = [o for o in orders if o and o[-1] != "DONE"]

        if not orders:
            await interaction.response.send_message(
                "❌ ไม่มีออเดอร์ค้าง",
                ephemeral=True
            )
            return

        msg = "📋 ORDER (ACTIVE)\n\n"

        for order in orders[:10]:

            try:
                # 🔒 SAFE UNPACK (future proof)
                order = list(order) + [None] * 6
                order_id, user, item, amount, roblox_user, status = order[:6]

                amount = amount or 1

            except:
                continue

            line = (
                f"🆔 {order_id} | 👤 {user} | "
                f"📦 {item} x{amount} | 🔄 {status}"
            )

            if roblox_user:
                line += f" | 🎮 {roblox_user}"

            msg += line + "\n"

        try:
            await interaction.response.send_message(msg, ephemeral=True)
        except Exception as e:
            print("[ADMIN] send error:", e)


# =====================
# 🧾 ADD PRODUCT MODAL (HARDENED)
# =====================
class AddModal(discord.ui.Modal, title="Add Product"):

    name = discord.ui.TextInput(label="ชื่อสินค้า", required=True)
    price = discord.ui.TextInput(label="ราคา", required=True)
    stock = discord.ui.TextInput(label="จำนวน", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        name = self.name.value.strip()

        try:
            price = float(self.price.value)
            qty = int(self.stock.value)
        except:
            await interaction.response.send_message(
                "❌ ข้อมูลไม่ถูกต้อง",
                ephemeral=True
            )
            return

        # 🔒 VALIDATION HARDENING
        if not name or price < 0 or qty <= 0:
            await interaction.response.send_message(
                "❌ ข้อมูลไม่ถูกต้อง (invalid range)",
                ephemeral=True
            )
            return

        try:
            success = self.bot.stock.add(name, qty, price)
        except Exception as e:
            print("[ADMIN] stock add error:", e)
            success = False

        if not success:
            await interaction.response.send_message(
                "❌ เพิ่มสินค้าไม่สำเร็จ",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"✅ เพิ่มสินค้าแล้ว\n📦 {name} | {qty} ชิ้น | {price} บาท",
            ephemeral=True
        )
