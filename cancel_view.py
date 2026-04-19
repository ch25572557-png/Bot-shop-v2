import discord


# =====================
# ❌ CANCEL SELECT
# =====================
class CancelSelect(discord.ui.Select):

    def __init__(self, bot):
        self.bot = bot

        options = []

        try:
            cur = bot.mem.conn.cursor()
            cur.execute("""
                SELECT id, item, amount, status
                FROM orders
                WHERE status != 'CANCELLED'
                ORDER BY id DESC
                LIMIT 25
            """)
            orders = cur.fetchall()

        except Exception as e:
            print("[CANCEL DB ERROR]", e)
            orders = []

        for o in orders:

            options.append(
                discord.SelectOption(
                    label=f"#{o[0]} | {o[1]} x{o[2]}",
                    value=str(o[0]),
                    description=f"status: {o[3]}"
                )
            )

        if not options:
            options = [
                discord.SelectOption(
                    label="ไม่มีออเดอร์",
                    value="none"
                )
            ]

        super().__init__(
            placeholder="❌ เลือกออเดอร์",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        order_id = self.values[0]

        if order_id == "none":
            return await interaction.response.send_message(
                "❌ ไม่มีออเดอร์",
                ephemeral=True
            )

        try:
            data = self.bot.mem.get_order(order_id)

            if not data:
                return await interaction.response.send_message(
                    "❌ ไม่พบออเดอร์",
                    ephemeral=True
                )

            user, item, amount, roblox_user, status = data

            if status == "DONE":
                return await interaction.response.send_message(
                    "❌ ออเดอร์เสร็จแล้ว",
                    ephemeral=True
                )

            if status == "CANCELLED":
                return await interaction.response.send_message(
                    "❌ ถูกยกเลิกแล้ว",
                    ephemeral=True
                )

            # =====================
            # ❌ UPDATE STATUS
            # =====================
            self.bot.mem.update_order_status(order_id, "CANCELLED")

            # =====================
            # 🔁 RETURN STOCK (SAFE SINGLE SOURCE)
            # =====================
            self.bot.mem.add_stock(item, amount)

            # =====================
            # 🎫 DELETE TICKET CHANNEL
            # =====================
            try:
                channel_id = self.bot.mem.get_ticket(order_id)

                if channel_id:
                    channel = self.bot.get_channel(int(channel_id))

                    if channel:
                        await channel.send("❌ ออเดอร์ถูกยกเลิก กำลังปิดห้อง...")
                        await discord.utils.sleep_until(discord.utils.utcnow())

                        await channel.delete(reason="Order cancelled")

            except Exception as e:
                print("[DELETE CHANNEL ERROR]", e)

            # =====================
            # 📢 NOTIFY ADMIN
            # =====================
            try:
                channel_id = self.bot.brain.channel("ORDER_NOTIFY")
                channel = self.bot.get_channel(int(channel_id)) if channel_id else None

                if channel:
                    embed = discord.Embed(
                        title="❌ ORDER CANCELLED",
                        description=f"Order #{order_id}\n{item} x{amount}",
                        color=0xff0000
                    )
                    await channel.send(embed=embed)

            except Exception as e:
                print("[NOTIFY ERROR]", e)

            await interaction.response.send_message(
                f"✅ ยกเลิกออเดอร์ #{order_id} แล้ว",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ error: {e}",
                ephemeral=True
            )


# =====================
# ❌ VIEW
# =====================
class CancelView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(CancelSelect(bot))
