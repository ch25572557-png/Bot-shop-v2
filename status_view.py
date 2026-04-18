import discord

class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_id = order_id

    # =====================
    # ⏳ WAIT ADMIN
    # =====================
    @discord.ui.button(label="⏳ รอแอดมินรับออเดอร์", style=discord.ButtonStyle.gray)
    async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            self.bot.mem.update_order_status(self.order_id, "WAIT_ADMIN")
        except Exception as e:
            print("[STATUS] wait_admin:", e)

        await interaction.response.send_message("⏳ WAIT_ADMIN", ephemeral=True)

    # =====================
    # 👨‍💼 ADMIN ACCEPT
    # =====================
    @discord.ui.button(label="👨‍💼 แอดมินรับออเดอร์แล้ว", style=discord.ButtonStyle.blurple)
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            self.bot.mem.update_order_status(self.order_id, "ADMIN_ACCEPTED")
        except Exception as e:
            print("[STATUS] admin_accept:", e)

        await interaction.response.send_message("👨‍💼 ADMIN_ACCEPTED", ephemeral=True)

    # =====================
    # 🪏 FARMING
    # =====================
    @discord.ui.button(label="🪏 กำลังฟาร์ม", style=discord.ButtonStyle.green)
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            self.bot.mem.update_order_status(self.order_id, "FARMING")
        except Exception as e:
            print("[STATUS] farming:", e)

        await interaction.response.send_message("🪏 FARMING", ephemeral=True)

    # =====================
    # 📦 WAIT CUSTOMER
    # =====================
    @discord.ui.button(label="📦 รอลูกค้ามารับของ", style=discord.ButtonStyle.gray)
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            self.bot.mem.update_order_status(self.order_id, "WAIT_CUSTOMER")
        except Exception as e:
            print("[STATUS] wait_customer:", e)

        await interaction.response.send_message("📦 WAIT_CUSTOMER", ephemeral=True)

    # =====================
    # ✅ DONE (FIXED + SAFE FINAL FLOW)
    # =====================
    @discord.ui.button(label="✅ ส่งของเสร็จแล้ว", style=discord.ButtonStyle.green)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        # =====================
        # 🔒 LOAD ORDER SAFE
        # =====================
        try:
            data = self.bot.mem.get_order(self.order_id)
            if not data:
                await interaction.response.send_message("❌ ไม่พบออเดอร์", ephemeral=True)
                return
        except Exception as e:
            print("[STATUS] get_order error:", e)
            return

        # =====================
        # 🔍 SAFE STATUS PARSE (support old/new schema)
        # =====================
        status = None

        try:
            data = list(data) + [None] * 5
            status = data[4]
        except:
            status = None

        # =====================
        # ❗ BLOCK DUPLICATE COMPLETE
        # =====================
        if status in ("DONE", "LOCKED"):
            await interaction.response.send_message("❗ ออเดอร์นี้เสร็จแล้ว", ephemeral=True)
            return

        # =====================
        # 🔄 USER FEEDBACK
        # =====================
        try:
            await interaction.response.send_message("🔄 กำลังจบออเดอร์...", ephemeral=True)
        except:
            pass

        # =====================
        # 🚀 CALL MAIN SYSTEM (SAFE WRAP)
        # =====================
        try:
            await self.bot.order.complete(interaction.channel)
        except Exception as e:
            print("[STATUS] complete error:", e)

            try:
                await interaction.channel.send("❌ error ตอน complete order")
            except:
                pass
