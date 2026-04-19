import discord
import asyncio


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

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        raw_id = self.values[0]

        if raw_id == "none":
            return await interaction.followup.send("❌ ไม่มีออเดอร์", ephemeral=True)

        try:
            order_id = int(raw_id)

            data = self.bot.mem.get_order(order_id)

            if not data:
                return await interaction.followup.send("❌ ไม่พบออเดอร์", ephemeral=True)

            user, item, amount, roblox_user, status = data

            if status in ["DONE", "CANCELLED"]:
                return await interaction.followup.send(
                    "❌ ออเดอร์นี้ใช้งานไม่ได้แล้ว",
                    ephemeral=True
                )

            # =====================
            # ❌ UPDATE STATUS
            # =====================
            self.bot.mem.update_order_status(order_id, "CANCELLED")

            # =====================
            # 🔁 RETURN STOCK
            # =====================
            self.bot.mem.add_stock(item, amount)

            # =====================
            # 🎫 DELETE CHANNEL (FIXED)
            # =====================
            try:
                channel_id = self.bot.mem.get_ticket(order_id)

                if channel_id:
                    channel = self.bot.get_channel(int(channel_id))

                    # 🔥 fallback (สำคัญมาก)
                    if not channel:
                        try:
                            channel = await self.bot.fetch_channel(int(channel_id))
                        except:
                            channel = None

                    if channel:
                        await channel.send("❌ ออเดอร์ถูกยกเลิก กำลังปิดห้อง...")
                        await asyncio.sleep(2)
                        await channel.delete(reason="Order cancelled")

            except Exception as e:
                print("[DELETE CHANNEL ERROR]", e)

            # =====================
            # 📢 NOTIFY ADMIN
            # =====================
            try:
                channel_id = self.bot.brain.channel("ORDER_NOTIFY")

                if channel_id:
                    ch = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)

                    if ch:
                        embed = discord.Embed(
                            title="❌ ORDER CANCELLED",
                            description=f"Order #{order_id}\n{item} x{amount}",
                            color=0xff0000
                        )
                        await ch.send(embed=embed)

            except Exception as e:
                print("[NOTIFY ERROR]", e)

            await interaction.followup.send(
                f"✅ ยกเลิกออเดอร์ #{order_id} แล้ว",
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ error: {e}",
                ephemeral=True
            )


class CancelView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(CancelSelect(bot))
