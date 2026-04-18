class NotifySystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 🔧 INTERNAL SAFE CHANNEL GETTER
    # =====================
    def _get_admin_channel(self):
        try:
            ch_id = self.brain.get("CHANNELS.ADMIN")
            if not ch_id:
                return None

            return self.bot.get_channel(int(ch_id))
        except:
            return None

    # =====================
    # 🔔 ADMIN NOTIFY (NEW ORDER)
    # =====================
    async def admin(self, user, item, order_id=None):

        ch = self._get_admin_channel()
        if not ch:
            return

        try:
            admin_role = self.brain.get("CHANNELS.ADMIN_ROLE")

            msg = (
                f"🔔 NEW ORDER\n"
                f"👤 User: {user.mention}\n"
                f"📦 Item: {item}"
            )

            if order_id:
                msg += f"\n🆔 Order ID: {order_id}"

            # 🔥 safe role ping
            if admin_role:
                msg = f"<@&{admin_role}>\n" + msg

            await ch.send(msg)

        except Exception as e:
            print("[NOTIFY] admin error:", e)

    # =====================
    # ✅ COMPLETE NOTIFY
    # =====================
    async def complete(self, user, item, order_id=None):

        ch = self._get_admin_channel()
        if not ch:
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

        except Exception as e:
            print("[NOTIFY] complete error:", e)

    # =====================
    # ⚠️ STOCK ALERT (FINAL SAFE VERSION)
    # =====================
    async def stock_alert(self, item, qty):

        ch = self._get_admin_channel()
        if not ch:
            return

        try:
            admin_role = self.brain.get("CHANNELS.ADMIN_ROLE")

            msg = (
                f"⚠️ STOCK ALERT\n"
                f"📦 Item: {item}\n"
                f"📉 Remaining: {qty}"
            )

            if admin_role:
                msg += f"\n<@&{admin_role}>"

            await ch.send(msg)

        except Exception as e:
            print("[NOTIFY] stock alert error:", e)
