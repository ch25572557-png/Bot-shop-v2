class NotifySystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 🔔 ADMIN NOTIFY (NEW ORDER)
    # =====================
    async def admin(self, user, item, order_id=None):

        try:
            ch_id = int(self.brain.get("CHANNELS.ADMIN"))
            ch = self.bot.get_channel(ch_id)
        except:
            ch = None

        if ch is None:
            return

        try:
            msg = (
                f"🔔 NEW ORDER\n"
                f"👤 User: {user.mention}\n"
                f"📦 Item: {item}"
            )

            if order_id:
                msg += f"\n🆔 Order ID: {order_id}"

            # 🟡 ping role admin (optional)
            msg = f"<@&{self.brain.get('CHANNELS.ADMIN_ROLE') or ''}>\n" + msg

            await ch.send(msg)

        except:
            pass

    # =====================
    # ✅ COMPLETE NOTIFY
    # =====================
    async def complete(self, user, item, order_id=None):

        try:
            ch_id = int(self.brain.get("CHANNELS.ADMIN"))
            ch = self.bot.get_channel(ch_id)
        except:
            ch = None

        if ch is None:
            return

        try:
            msg = (
                f"✅ ORDER COMPLETE\n"
                f"👤 User: {user}\n"
                f"📦 Item: {item}"
            )

            if order_id:
                msg += f"\n🆔 Order ID: {order_id}"

            await ch.send(msg)

        except:
            pass

    # =====================
    # ⚠️ STOCK ALERT NOTIFY (NEW)
    # =====================
    async def stock_alert(self, item, qty):

        try:
            ch_id = int(self.brain.get("CHANNELS.ADMIN"))
            ch = self.bot.get_channel(ch_id)
        except:
            ch = None

        if ch is None:
            return

        try:
            msg = (
                f"⚠️ STOCK ALERT\n"
                f"📦 Item: {item}\n"
                f"📉 Remaining: {qty}\n"
                f"<@&{self.brain.get('CHANNELS.ADMIN_ROLE') or ''}>"
            )

            await ch.send(msg)

        except:
            pass
