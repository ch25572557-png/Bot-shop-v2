async def log(self, message):
    try:
        ch_id = self.brain.get("CHANNELS.BACKUP")
        channel = self.bot.get_channel(int(ch_id))

        if channel is None:
            return

        await channel.send(f"💾 BACKUP\n{message}")

    except Exception as e:
        print(f"[BACKUP ERROR] {e}")
