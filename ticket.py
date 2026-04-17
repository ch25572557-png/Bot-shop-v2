import discord
from status_view import StatusView

class TicketSystem:
    def __init__(self, brain, bot):
        self.brain = brain
        self.bot = bot

    async def create(self, guild, user, order_id):

        category = guild.get_channel(
            int(self.brain.get("CHANNELS.TICKET_CATEGORY"))
        )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{order_id}-{user.name}",
            category=category,
            overwrites=overwrites
        )

        # 💾 link ticket → order
        self.bot.mem.cur.execute(
            "INSERT INTO tickets VALUES(?,?)",
            (order_id, str(channel.id))
        )
        self.bot.mem.conn.commit()

        await channel.send(
            f"🎫 Ticket for ORDER #{order_id}",
            view=StatusView(self.bot, order_id)
        )

        return channel
