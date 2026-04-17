class NotifySystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    async def admin(self, user, item):
        ch = self.bot.get_channel(
            int(self.brain.get("CHANNELS.ADMIN"))
        )

        await ch.send(
            f"🔔 NEW ORDER\nUser: {user}\nItem: {item}"
        )
