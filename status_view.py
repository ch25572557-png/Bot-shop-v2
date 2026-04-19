import discord

# =====================
# ⏳ WAIT ADMIN
# =====================
async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):

    await interaction.response.defer(ephemeral=True)

    await self.bot.mem.update_order_status(self.order_id, "WAIT_ADMIN")
    await self.send_ticket(interaction, "WAIT_ADMIN")

    await interaction.followup.send("✅ WAIT_ADMIN", ephemeral=True)


# =====================
# 👨‍💼 ACCEPT
# =====================
async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):

    await interaction.response.defer(ephemeral=True)

    await self.bot.mem.update_order_status(self.order_id, "ADMIN_ACCEPTED")
    await self.send_ticket(interaction, "ADMIN_ACCEPTED")

    await interaction.followup.send("✅ รับออเดอร์แล้ว", ephemeral=True)


# =====================
# 🪏 FARMING
# =====================
async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):

    await interaction.response.defer(ephemeral=True)

    await self.bot.mem.update_order_status(self.order_id, "FARMING")
    await self.send_ticket(interaction, "FARMING")

    await interaction.followup.send("🪏 ฟาร์มแล้ว", ephemeral=True)


# =====================
# 📦 WAIT CUSTOMER
# =====================
async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):

    await interaction.response.defer(ephemeral=True)

    await self.bot.mem.update_order_status(self.order_id, "WAIT_CUSTOMER")
    await self.send_ticket(interaction, "WAIT_CUSTOMER")

    await interaction.followup.send("📦 รอลูกค้า", ephemeral=True)


# =====================
# ✅ DONE (FIXED)
# =====================
async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

    await interaction.response.defer(ephemeral=True)

    try:
        if not interaction.channel:
            return await interaction.followup.send("❌ ไม่พบ channel", ephemeral=True)

        success = await self.bot.order.complete(interaction.channel)

        if success:
            await interaction.followup.send("✅ ปิดออเดอร์แล้ว", ephemeral=True)
        else:
            await interaction.followup.send("❌ ปิดไม่สำเร็จ", ephemeral=True)

    except Exception as e:
        print("[STATUS COMPLETE ERROR]", e)
        await interaction.followup.send("❌ ERROR", ephemeral=True)
