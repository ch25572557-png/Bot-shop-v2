import discord
from utils import safe_send


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
            print("[CANCEL SELECT DB ERROR]", e)
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
            # 🔁 RETURN STOCK (SAFE)
            # =====================
            try:
                if hasattr(self.bot.stock, "add"):
                    self.bot.stock.add(item, amount, 0)
                else:
                    cur = self.bot.mem.conn.cursor()
                    cur.execute(
                        "UPDATE stock SET qty = qty + ? WHERE name=?",
                        (amount, item)
                    )
                    self.bot.mem.conn.commit()

            except Exception as e:
                print("[STOCK RETURN ERROR]", e)

            # =====================
            # 📢 NOTIFY (SAFE)
            # =====================
            try:
                channel_id = self.bot.brain.channel("ORDER_NOTIFY")

                channel = self.bot.get_channel(int(channel_id)) if channel_id else None

                if channel:
                    embed = discord.Embed(
                        title="❌ ORDER CANCELLED",
                        description=f"Order #{order_id}\nItem: {item} x{amount}",
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
