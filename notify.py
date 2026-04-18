class NotifySystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    # =====================
    # 🔔 ADMIN NOTIFY
    # =====================
    async def admin(self, user, item, order_id=None):

        # 🧠 ดึง channel
        try:
            ch_id = int(self.brain.get("CHANNELS.ADMIN"))
            ch = self.bot.get_channel(ch_id)
        except:
            ch = None

        # 🛡 กัน channel หาย
        if ch is None:
            return

        # 📢 สร้างข้อความ
        try:
            msg = (
                f"🔔 NEW ORDER\n"
                f"👤 User: {user.mention}\n"
                f"📦 Item: {item}"
            )

            if order_id:
                msg += f"\n🆔 Order ID: {order_id}"

            await ch.send(msg)

        except:
            pass

    # =====================
    # ✅ COMPLETE NOTIFY (เผื่อใช้ต่อ)
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
