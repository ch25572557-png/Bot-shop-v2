import discord
import asyncio
import time


class StatusView(discord.ui.View):

    def __init__(self, bot, order_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.order_id = order_id
        self._lock = asyncio.Lock()

        # 🔥 anti spam
        self.cooldown = {}

    # =====================
    # 🔐 ADMIN CHECK
    # =====================
    def is_admin(self, interaction: discord.Interaction):

        try:
            role_id = self.bot.brain.role("ADMIN_ROLE")
            if not role_id:
                return False

            role = interaction.guild.get_role(int(role_id))
            return role and role in interaction.user.roles

        except:
            return False

    # =====================
    # 🧠 GET ORDER
    # =====================
    async def get_order_id(self, interaction):
        return await self.bot.mem.get_order_by_channel(str(interaction.channel.id))

    # =====================
    # 🚫 SPAM PROTECTION
    # =====================
    def check_cooldown(self, user_id):
        now = time.time()

        if user_id in self.cooldown:
            if now - self.cooldown[user_id] < 2:
                return False

        self.cooldown[user_id] = now
        return True

    # =====================
    # 💾 UPDATE STATUS (SAFE)
    # =====================
    async def send_ticket(self, interaction, status):

        async with self._lock:

            try:
                order_id = await self.get_order_id(interaction)
                if not order_id:
                    return False

                # 🔥 check status ซ้ำ
                data = await self.bot.mem.get_order(order_id)
                if data:
                    _, _, _, _, current_status = data
                    if current_status == status:
                        return False

                await self.bot.mem.update_order_status(order_id, status)

                await interaction.channel.send(
                    embed=discord.Embed(
                        title="📊 STATUS UPDATE",
                        description=f"Order #{order_id}\nสถานะ: `{status}`",
                        color=0x00ffcc
                    )
                )

                print(f"[STATUS] {order_id} -> {status} by {interaction.user}")

                return True

            except Exception as e:
                print("[STATUS ERROR]", e)
                return False

    # =====================
    # ⏳ WAIT ADMIN
    # =====================
    @discord.ui.button(label="⏳ WAIT ADMIN", style=discord.ButtonStyle.gray, custom_id="wait_admin")
    async def wait_admin(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ แอดมินเท่านั้น", ephemeral=True)

        if not self.check_cooldown(interaction.user.id):
            return await interaction.response.send_message("⏳ กดเร็วเกินไป", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        ok = await self.send_ticket(interaction, "WAIT_ADMIN")

        if ok:
            await interaction.followup.send("✅ WAIT_ADMIN", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ สถานะซ้ำ", ephemeral=True)

    # =====================
    # 👨‍💼 ACCEPT
    # =====================
    @discord.ui.button(label="👨‍💼 ACCEPT", style=discord.ButtonStyle.green, custom_id="admin_accept")
    async def admin_accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ แอดมินเท่านั้น", ephemeral=True)

        if not self.check_cooldown(interaction.user.id):
            return await interaction.response.send_message("⏳ กดเร็วเกินไป", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        ok = await self.send_ticket(interaction, "ADMIN_ACCEPTED")

        if ok:
            await interaction.followup.send("✅ รับออเดอร์แล้ว", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ สถานะซ้ำ", ephemeral=True)

    # =====================
    # 🪏 FARMING
    # =====================
    @discord.ui.button(label="🪏 FARMING", style=discord.ButtonStyle.blurple, custom_id="farming")
    async def farming(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ แอดมินเท่านั้น", ephemeral=True)

        if not self.check_cooldown(interaction.user.id):
            return await interaction.response.send_message("⏳ กดเร็วเกินไป", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        ok = await self.send_ticket(interaction, "FARMING")

        if ok:
            await interaction.followup.send("🪏 กำลังฟาร์ม", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ สถานะซ้ำ", ephemeral=True)

    # =====================
    # 📦 WAIT CUSTOMER
    # =====================
    @discord.ui.button(label="📦 WAIT CUSTOMER", style=discord.ButtonStyle.gray, custom_id="wait_customer")
    async def waiting_customer(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ แอดมินเท่านั้น", ephemeral=True)

        if not self.check_cooldown(interaction.user.id):
            return await interaction.response.send_message("⏳ กดเร็วเกินไป", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        ok = await self.send_ticket(interaction, "WAIT_CUSTOMER")

        if ok:
            await interaction.followup.send("📦 รอลูกค้า", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ สถานะซ้ำ", ephemeral=True)

    # =====================
    # ✅ DONE
    # =====================
    @discord.ui.button(label="✅ DONE", style=discord.ButtonStyle.green, custom_id="done")
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ แอดมินเท่านั้น", ephemeral=True)

        if not self.check_cooldown(interaction.user.id):
            return await interaction.response.send_message("⏳ กดเร็วเกินไป", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        try:
            success = await self.bot.order.complete(interaction.channel)

            if success:
                await self.send_ticket(interaction, "DONE")
                await interaction.followup.send("✅ ปิดออเดอร์แล้ว", ephemeral=True)
            else:
                await interaction.followup.send("❌ ปิดไม่สำเร็จ", ephemeral=True)

        except Exception as e:
            print("[DONE ERROR]", e)
            await interaction.followup.send("❌ ERROR", ephemeral=True)
