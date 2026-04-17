class BackupSystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    async def log(self, message):
        try:
            ch_id = self.brain.get("CHANNELS.BACKUP")
            channel = self.bot.get_channel(int(ch_id))
            await channel.send(f"💾 BACKUP\n{message}")
        except:
            pass
