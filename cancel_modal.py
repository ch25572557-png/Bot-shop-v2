import discord

class CancelOrderModal(discord.ui.Modal, title="❌ Cancel Order"):

    order_id = discord.ui.TextInput(
        label="Order ID",
        placeholder="ใส่เลข Order เช่น 1234",
        required=True
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):

        order_id = self.order_id.value.strip()

        try:
            data = self.bot.mem.get_order(order_id)

            if not data:
                return await interaction.response.send_message(
                    "❌ ไม่พบ Order",
                    ephemeral=True
                )

            user, item, amount, roblox_user, status = data

            if status == "DONE":
                return await interaction.response.send_message(
                    "❌ Order นี้เสร็จแล้ว",
                    ephemeral=True
                )

            # 🔥 update order
            self.bot.mem.update_order_status(order_id, "CANCELLED")

            # 🔥 return stock
            cur = self.bot.mem.conn.cursor()
            cur.execute(
                "UPDATE stock SET qty = qty + ? WHERE name=?",
                (amount, item)
            )
            self.bot.mem.conn.commit()

            # 🔥 notify admin
            ch_id = self.bot.brain.get("CHANNELS.ORDER_NOTIFY")
            if ch_id:
                channel = self.bot.get_channel(int(ch_id))
                if channel:
                    embed = discord.Embed(
                        title="❌ ORDER CANCELLED",
                        description=f"Order #{order_id}\nUser: {user}\nItem: {item} x{amount}",
                        color=0xff0000
                    )
                    await channel.send(embed=embed)

            await interaction.response.send_message(
                "✅ ยกเลิกสำเร็จ",
                ephemeral=True
            )

        except Exception as e:
            print("[CANCEL ERROR]", e)
            await interaction.response.send_message(
                "❌ error",
                ephemeral=True
            )
