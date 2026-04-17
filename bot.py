import discord
import os

from core.brain import Brain
from core.memory import Memory

from systems.ticket import TicketSystem
from systems.stock import StockSystem
from systems.notify import NotifySystem
from systems.order import OrderSystem
from systems.backup import BackupSystem

from ui.shop import ShopView
from ui.admin import AdminView

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

# CORE
bot.brain = Brain()
bot.mem = Memory()
bot.backup = BackupSystem(bot.brain, bot)

# SYSTEMS
bot.stock = StockSystem(bot.mem)
bot.ticket = TicketSystem(bot.brain)
bot.notify = NotifySystem(bot.brain, bot)
bot.order = OrderSystem(bot.mem, bot.ticket, bot.notify, bot.backup)

@bot.event
async def on_ready():
    print("🟢 FULL FINAL SHOP SYSTEM READY")

@bot.event
async def on_message(message):

    if message.content == "!shop":
        await message.channel.send("🛒 SHOP ONLINE", view=ShopView(bot))

    if message.content == "!admin":
        await message.channel.send("🛠 ADMIN PANEL", view=AdminView(bot))

bot.run(os.getenv("TOKEN"))
