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
            cur.execute("SELECT id, item, amount, status FROM orders WHERE status!='CANCELLED' ORDER BY id DESC LIMIT 25")
            orders = cur.fetchall()
        except:
            orders = []

        for o in orders:
            order_id = str(o[0])
            item = o[1]
            amount = o[2]
            status = o[3]

            options.append(
                discord.SelectOption(
                    label=f"#{order_id} | {item} x{amount}",
                    value=order_id,
                    description=f"status: {status}"
                )
            )

        if not options:
            options = [
                discord.SelectOption(
                    label="ไม่มีออเดอร์ให้ยกเลิก",
                    value="none"
                )
            ]

        super().__init__(
            placeholder="❌ เลือกออเดอร์ที่ต้องการยกเลิก",
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
                    "❌ ออเดอร์นี้เสร็จแล้ว",
                    ephemeral=True
                )

            # =====================
            # ❌ CANCEL ORDER
            # =====================
            self.bot.mem.update_order_status(order_id, "CANCELLED")

            # =====================
            # 🔁 RETURN STOCK
            # =====================
            if hasattr(self.bot.stock, "add"):
                self.bot.stock.add(item, amount, 0)

            else:
                cur = self.bot.mem.conn.cursor()
                cur.execute(
                    "UPDATE stock SET qty = qty + ? WHERE name=?",
                    (amount, item)
                )
                self.bot.mem.conn.commit()

            # =====================
            # 📢 NOTIFY
            # =====================
            try:
                ch_id = self.bot.brain.get("CHANNELS.ORDER_NOTIFY")

                if ch_id:
                    channel = self.bot.get_channel(int(ch_id))

                    if channel:
                        embed = discord.Embed(
                            title="❌ ORDER CANCELLED",
                            description=f"Order #{order_id}\nItem: {item} x{amount}",
                            color=0xff0000
                        )
                        await channel.send(embed=embed)

            except:
                pass

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
