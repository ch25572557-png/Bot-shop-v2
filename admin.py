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
    # 📋 VIEW ORDERS (FILTER DONE)
    # =====================
    @discord.ui.button(label="📋 ดูออเดอร์", style=discord.ButtonStyle.blurple)
    async def view_orders(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            orders = self.bot.mem.get_all_orders()
        except Exception as e:
            print("[ADMIN] get orders error:", e)
            orders = []

        # 🔥 filter DONE
        try:
            orders = [o for o in orders if o[-1] != "DONE"]
        except:
            pass

        if not orders:
            await interaction.response.send_message(
                "❌ ไม่มีออเดอร์ค้าง",
                ephemeral=True
            )
            return

        msg = "📋 ORDER (ACTIVE)\n\n"

        # 📦 limit safe
        for order in orders[:10]:

            try:
                order_id, user, item, amount, roblox_user, status = order
            except:
                try:
                    order_id, user, item, status = order
                except:
                    continue

                amount = 1
                roblox_user = None

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
# 🧾 ADD PRODUCT MODAL
# =====================
class AddModal(discord.ui.Modal, title="Add Product"):

    name = discord.ui.TextInput(label="ชื่อสินค้า", required=True)
    price = discord.ui.TextInput(label="ราคา", required=True)
    stock = discord.ui.TextInput(label="จำนวน", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        # =====================
        # 🛡 SAFE INPUT
        # =====================
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

        if not name:
            await interaction.response.send_message(
                "❌ ชื่อสินค้าไม่ถูกต้อง",
                ephemeral=True
            )
            return

        # =====================
        # 📦 ADD STOCK
        # =====================
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

        # =====================
        # ✅ SUCCESS
        # =====================
        await interaction.response.send_message(
            f"✅ เพิ่มสินค้าแล้ว\n📦 {name} | {qty} ชิ้น | {price} บาท",
            ephemeral=True
        )
