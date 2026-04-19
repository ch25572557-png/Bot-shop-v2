import discord
import asyncio


class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_id = order_id
        self._lock = asyncio.Lock()

    # =====================
    # 💾 UPDATE STATUS CORE (FIXED)
    # =====================
    async def send_ticket(self, status):

        async with self._lock:

            try:
                await self.bot.mem.update_order_status(self.order_id, status)

                channel_id = await self.bot.mem.get_ticket(self.order_id)
                if not channel_id:
                    return

                channel_id = int(channel_id)

                channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)

                if not channel:
                    return

                embed = discord.Embed(
                    title="📊 STATUS UPDATE",
                    description=f"Order #{self.order_id}\nสถานะ: `{status}`",
                    color=0x00ffcc
                )

                await channel.send(embed=embed)

                print(f"[STATUS] {self.order_id} -> {status}")

            except Exception as e:
                print("[STATUS SEND ERROR]", e)

    # =====================
    # 🔐 PERMISSION CHECK
    # =====================
    def is_admin(self, user):
        return user.guild_permissions.administrator or user.guild_permissions.manage_guild

    # =====================
    # ⏳ WAIT ADMIN
    # =====================
    @discord.ui.button(label="⏳ WAIT ADMIN", style=discord.ButtonStyle.gray, custom_id="wait_admin")
    async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.bot:
            return

        await self.send_ticket("WAIT_ADMIN")

        await interaction.response.send_message("✅ WAIT_ADMIN", ephemeral=True)

    # =====================
    # 👨‍💼 ACCEPT
    # =====================
    @discord.ui.button(label="👨‍💼 ACCEPT", style=discord.ButtonStyle.green, custom_id="admin_accept")
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.bot:
            return

        if not self.is_admin(interaction.user):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        await self.send_ticket("ADMIN_ACCEPTED")

        await interaction.response.send_message("✅ รับออเดอร์แล้ว", ephemeral=True)

    # =====================
    # 🪏 FARMING
    # =====================
    @discord.ui.button(label="🪏 FARMING", style=discord.ButtonStyle.blurple, custom_id="farming")
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.bot:
            return

        await self.send_ticket("FARMING")

        await interaction.response.send_message("🪏 ฟาร์มแล้ว", ephemeral=True)

    # =====================
    # 📦 WAIT CUSTOMER
    # =====================
    @discord.ui.button(label="📦 WAIT CUSTOMER", style=discord.ButtonStyle.gray, custom_id="wait_customer")
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.bot:
            return

        await self.send_ticket("WAIT_CUSTOMER")

        await interaction.response.send_message("📦 รอลูกค้า", ephemeral=True)

    # =====================
    # ✅ DONE (FIXED FLOW)
    # =====================
    @discord.ui.button(label="✅ DONE", style=discord.ButtonStyle.green, custom_id="done")
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.bot:
            return

        if not self.is_admin(interaction.user):
            return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        try:
            success = await self.bot.order.complete(interaction.channel)

            if success:
                await self.send_ticket("DONE")
                await interaction.followup.send("✅ ปิดออเดอร์แล้ว", ephemeral=True)
            else:
                await interaction.followup.send("❌ ปิดไม่สำเร็จ", ephemeral=True)

        except Exception as e:
            print("[STATUS DONE ERROR]", e)
            await interaction.followup.send("❌ ERROR", ephemeral=True)
