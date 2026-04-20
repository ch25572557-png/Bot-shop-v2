import discord
import asyncio


class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_id = order_id
        self._lock = asyncio.Lock()

    # =====================
    # 🔐 ADMIN CHECK (FIXED)
    # =====================
    def is_admin(self, interaction):

        role_id = self.bot.brain.role("ADMIN_ROLE")
        if not role_id:
            return False

        role = interaction.guild.get_role(int(role_id))
        return role in interaction.user.roles

    # =====================
    # 💾 UPDATE STATUS
    # =====================
    async def send_ticket(self, status):

        async with self._lock:

            try:
                await self.bot.mem.update_order_status(self.order_id, status)

                channel_id = await self.bot.mem.get_ticket(self.order_id)
                if not channel_id:
                    return

                channel = self.bot.get_channel(int(channel_id)) or await self.bot.fetch_channel(int(channel_id))
                if not channel:
                    return

                await channel.send(
                    embed=discord.Embed(
                        title="📊 STATUS UPDATE",
                        description=f"Order #{self.order_id}\nสถานะ: `{status}`",
                        color=0x00ffcc
                    )
                )

                print(f"[STATUS] {self.order_id} -> {status}")

            except Exception as e:
                print("[STATUS ERROR]", e)

    # =====================
    # ⏳ WAIT ADMIN
    # =====================
    @discord.ui.button(label="⏳ WAIT ADMIN", style=discord.ButtonStyle.gray, custom_id="wait_admin")
    async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ แอดมินเท่านั้น", ephemeral=True)

        await self.send_ticket("WAIT_ADMIN")
        await interaction.response.send_message("✅ WAIT_ADMIN", ephemeral=True)

    # =====================
    # 👨‍💼 ACCEPT
    # =====================
    @discord.ui.button(label="👨‍💼 ACCEPT", style=discord.ButtonStyle.green, custom_id="admin_accept")
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ แอดมินเท่านั้น", ephemeral=True)

        await self.send_ticket("ADMIN_ACCEPTED")
        await interaction.response.send_message("✅ รับออเดอร์แล้ว", ephemeral=True)

    # =====================
    # 🪏 FARMING
    # =====================
    @discord.ui.button(label="🪏 FARMING", style=discord.ButtonStyle.blurple, custom_id="farming")
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ แอดมินเท่านั้น", ephemeral=True)

        await self.send_ticket("FARMING")
        await interaction.response.send_message("🪏 กำลังฟาร์ม", ephemeral=True)

    # =====================
    # 📦 WAIT CUSTOMER
    # =====================
    @discord.ui.button(label="📦 WAIT CUSTOMER", style=discord.ButtonStyle.gray, custom_id="wait_customer")
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ แอดมินเท่านั้น", ephemeral=True)

        await self.send_ticket("WAIT_CUSTOMER")
        await interaction.response.send_message("📦 รอลูกค้า", ephemeral=True)

    # =====================
    # ✅ DONE
    # =====================
    @discord.ui.button(label="✅ DONE", style=discord.ButtonStyle.green, custom_id="done")
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ แอดมินเท่านั้น", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        try:
            success = await self.bot.order.complete(interaction.channel)

            if success:
                await self.send_ticket("DONE")
                await interaction.followup.send("✅ ปิดออเดอร์แล้ว", ephemeral=True)
            else:
                await interaction.followup.send("❌ ปิดไม่สำเร็จ", ephemeral=True)

        except Exception as e:
            print("[DONE ERROR]", e)
            await interaction.followup.send("❌ ERROR", ephemeral=True)
