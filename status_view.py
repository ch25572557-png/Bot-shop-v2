import discord


class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_id = order_id

    # =====================
    # 💾 UPDATE STATUS CORE
    # =====================
    async def send_ticket(self, interaction, status):

        await self.bot.mem.update_order_status(self.order_id, status)

        try:
            channel_id = await self.bot.mem.get_ticket(self.order_id)

            if channel_id:
                channel = self.bot.get_channel(int(channel_id)) or await self.bot.fetch_channel(int(channel_id))

                embed = discord.Embed(
                    title="📊 STATUS UPDATE",
                    description=f"สถานะ: `{status}`",
                    color=0x00ffcc
                )

                await channel.send(embed=embed)

        except Exception as e:
            print("[STATUS SEND ERROR]", e)

    # =====================
    # ⏳ WAIT ADMIN
    # =====================
    @discord.ui.button(label="⏳ WAIT ADMIN", style=discord.ButtonStyle.gray, custom_id="wait_admin")
    async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        await self.send_ticket(interaction, "WAIT_ADMIN")

        await interaction.followup.send("✅ WAIT_ADMIN", ephemeral=True)

    # =====================
    # 👨‍💼 ACCEPT
    # =====================
    @discord.ui.button(label="👨‍💼 ACCEPT", style=discord.ButtonStyle.green, custom_id="admin_accept")
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        await self.send_ticket(interaction, "ADMIN_ACCEPTED")

        await interaction.followup.send("✅ รับออเดอร์แล้ว", ephemeral=True)

    # =====================
    # 🪏 FARMING
    # =====================
    @discord.ui.button(label="🪏 FARMING", style=discord.ButtonStyle.blurple, custom_id="farming")
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        await self.send_ticket(interaction, "FARMING")

        await interaction.followup.send("🪏 ฟาร์มแล้ว", ephemeral=True)

    # =====================
    # 📦 WAIT CUSTOMER
    # =====================
    @discord.ui.button(label="📦 WAIT CUSTOMER", style=discord.ButtonStyle.gray, custom_id="wait_customer")
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        await self.send_ticket(interaction, "WAIT_CUSTOMER")

        await interaction.followup.send("📦 รอลูกค้า", ephemeral=True)

    # =====================
    # ✅ DONE
    # =====================
    @discord.ui.button(label="✅ DONE", style=discord.ButtonStyle.green, custom_id="done")
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        try:
            if not interaction.channel:
                return await interaction.followup.send("❌ ไม่พบ channel", ephemeral=True)

            success = await self.bot.order.complete(interaction.channel)

            if success:
                await self.send_ticket(interaction, "DONE")
                await interaction.followup.send("✅ ปิดออเดอร์แล้ว", ephemeral=True)
            else:
                await interaction.followup.send("❌ ปิดไม่สำเร็จ", ephemeral=True)

        except Exception as e:
            print("[STATUS DONE ERROR]", e)
            await interaction.followup.send("❌ ERROR", ephemeral=True)
