import discord
import os

from brain import Brain
from memory import Memory

from ticket import TicketSystem
from stock import StockSystem
from notify import NotifySystem
from order import OrderSystem
from backup import BackupSystem
from status import StatusSystem

from shop import ShopView
from admin import AdminView

# 🔥 INTENTS
intents = discord.Intents.all()
bot = discord.Client(intents=intents)

# 🧠 CORE
bot.brain = Brain()
bot.mem = Memory()

# 📦 SYSTEMS
bot.stock = StockSystem(bot.mem)
bot.ticket = TicketSystem(bot.brain)
bot.notify = NotifySystem(bot.brain, bot)

# 💾 BACKUP
bot.backup = BackupSystem(bot.brain, bot)

# 📊 STATUS
bot.status = StatusSystem(bot.mem)

# 🛒 ORDER
bot.order = OrderSystem(
    bot.mem,
    bot.ticket,
    bot.notify,
    bot.backup
)

# 🚀 READY
@bot.event
async def on_ready():
    print("🟢 FULL SHOP SYSTEM ONLINE")

# 💬 COMMANDS
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.content == "!shop":
        await message.channel.send("🛒 SHOP ONLINE", view=ShopView(bot))

    if message.content == "!admin":
        await message.channel.send("🛠 ADMIN PANEL", view=AdminView(bot))

# 🚀 RUN
bot.run(os.getenv("DISCORD_TOKEN"))
