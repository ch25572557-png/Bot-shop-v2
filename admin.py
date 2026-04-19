import discord

# =====================
# 🧾 MODALS
# =====================

class AddModal(discord.ui.Modal, title="➕ เพิ่มสินค้า"):

    name = discord.ui.TextInput(label="ชื่อสินค้า")
    price = discord.ui.TextInput(label="ราคา")
    stock = discord.ui.TextInput(label="จำนวน")

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        try:
            name = self.name.value.strip()
            price = float(self.price.value)
            qty = int(self.stock.value)

            if price < 0 or qty <= 0:
                raise ValueError

            self.bot.stock.add(name, qty, price)

            await interaction.response.send_message(
                f"✅ เพิ่มสินค้า {name}",
                ephemeral=True
            )

        except:
            await interaction.response.send_message("❌ ข้อมูลไม่ถูกต้อง", ephemeral=True)


class CancelModal(discord.ui.Modal, title="❌ ยกเลิกออเดอร์"):

    order_id = discord.ui.TextInput(label="Order ID")

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        try:
            order_id = int(self.order_id.value)
            order = self.bot.mem.get_order(order_id)

            if not order:
                return await interaction.response.send_message("❌ ไม่พบออเดอร์", ephemeral=True)

            user, item, amount, _, status = order

            self.bot.mem.update_order_status(order_id, "CANCELLED")
            self.bot.mem.add_stock(item, amount)

            # 🔥 ปิดห้องด้วย
            try:
                ch_id = self.bot.mem.get_ticket(order_id)
                if ch_id:
                    ch = self.bot.get_channel(int(ch_id))
                    if ch:
                        await ch.delete()
            except:
                pass

            await interaction.response.send_message(
                f"✅ ยกเลิกออเดอร์ #{order_id}",
                ephemeral=True
            )

        except:
            await interaction.response.send_message("❌ error", ephemeral=True)


class RestockModal(discord.ui.Modal, title="🔄 รีสต็อก"):

    name = discord.ui.TextInput(label="ชื่อสินค้า")
    amount = discord.ui.TextInput(label="จำนวน")

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        try:
            name = self.name.value.strip()
            qty = int(self.amount.value)

            if qty <= 0:
                raise ValueError

            self.bot.mem.add_stock(name, qty)

            await interaction.response.send_message(
                f"✅ รีสต็อก {name} +{qty}",
                ephemeral=True
            )

        except:
            await interaction.response.send_message("❌ ข้อมูลผิด", ephemeral=True)


# =====================
# 👑 ADMIN VIEW (PERSISTENT)
# =====================

class AdminView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    def is_admin(self, interaction):

        try:
            role_id = self.bot.brain.role("ADMIN_ROLE")
            return any(r.id == int(role_id) for r in interaction.user.roles)
        except:
            return False

    # ➕ ADD
    @discord.ui.button(
        label="➕ เพิ่มสินค้า",
        style=discord.ButtonStyle.green,
        custom_id="admin_add"
    )
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        await interaction.response.send_modal(AddModal(self.bot))

    # ❌ CANCEL
    @discord.ui.button(
        label="❌ ยกเลิกออเดอร์",
        style=discord.ButtonStyle.red,
        custom_id="admin_cancel"
    )
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        await interaction.response.send_modal(CancelModal(self.bot))

    # 🔄 RESTOCK
    @discord.ui.button(
        label="🔄 รีสต็อก",
        style=discord.ButtonStyle.blurple,
        custom_id="admin_restock"
    )
    async def restock(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        await interaction.response.send_modal(RestockModal(self.bot))

    # 📊 VIEW STOCK
    @discord.ui.button(
        label="📊 ดูสต๊อก",
        style=discord.ButtonStyle.gray,
        custom_id="admin_stock"
    )
    async def view_stock(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        try:
            cur = self.bot.mem.conn.execute(
                "SELECT name, qty, price FROM stock"
            )
            data = cur.fetchall()
        except:
            data = []

        if not data:
            return await interaction.response.send_message("❌ ไม่มีสต๊อก", ephemeral=True)

        msg = "\n".join([f"{n} | {q} | {p}" for n, q, p in data[:15]])

        await interaction.response.send_message(
            f"📦 STOCK\n\n{msg}",
            ephemeral=True
        )
