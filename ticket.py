import discord
from ui.status_view import StatusView

class TicketSystem:
    def __init__(self, brain):
        self.brain = brain

    async def create(self, guild, user, reason="order"):

        try:
            category = guild.get_channel(
                int(self.brain.get("CHANNELS.TICKET_CATEGORY"))
            )
        except:
            category = None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites=overwrites
        )

        # ✔ ต้องอยู่ใน block เดียวกัน
        await channel.send(
            f"🎫 Ticket created for {user.mention}",
            view=StatusView(self)
        )

        return channel
