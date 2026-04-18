class NotifySystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 🔧 GET ADMIN CHANNEL (SAFE FIXED)
    # =====================
    def _get_admin_channel(self):
        try:
            ch_id = self.brain.get("CHANNELS.ORDER_CHANNEL")
            if not ch_id:
                return None

            return self.bot.get_channel(int(ch_id))
        except:
            return None

    # =====================
    # 🔔 NEW ORDER NOTIFY (FIXED + SAFE ROLE)
    # =====================
    async def admin(self, user, item, order_id=None):

        ch = self._get_admin_channel()
        if not ch:
            return

        try:
            role_id = self.brain.get("ROLES.ADMIN_ROLE")

            msg = (
                f"🔔 NEW ORDER\n"
                f"👤 User: {getattr(user, 'mention', str(user))}\n"
                f"📦 Item: {item}"
            )

            if order_id:
                msg += f"\n🆔 Order ID: {order_id}"

            # 🔥 safe role ping
            if role_id:
                msg = f"<@&{role_id}>\n" + msg

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
                f"👤 User: {getattr(user, 'mention', str(user))}\n"
                f"📦 Item: {item}"
            )

            if order_id:
                msg += f"\n🆔 Order ID: {order_id}"

            await ch.send(msg)

        except Exception as e:
            print("[NOTIFY] complete error:", e)

    # =====================
    # ⚠️ STOCK ALERT (SAFE + ROLE FIX)
    # =====================
    async def stock_alert(self, item, qty):

        ch = self._get_admin_channel()
        if not ch:
            return

        try:
            role_id = self.brain.get("ROLES.ADMIN_ROLE")

            msg = (
                f"⚠️ STOCK ALERT\n"
                f"📦 Item: {item}\n"
                f"📉 Remaining: {qty}"
            )

            if role_id:
                msg += f"\n<@&{role_id}>"

            await ch.send(msg)

        except Exception as e:
            print("[NOTIFY] stock alert error:", e)
