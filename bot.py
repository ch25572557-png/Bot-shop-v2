import discord
import os

from core.brain import Brain
from core.memory import Memory

from systems.ticket import TicketSystem
from systems.stock import StockSystem
from systems.notify import NotifySystem
from systems.order import OrderSystem
from systems.backup import BackupSystem
from systems.status import StatusSystem

from ui.shop import ShopView
from ui.admin import AdminView

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

# 🧠 CORE
bot.brain = Brain()
bot.mem = Memory()

# 📦 SYSTEMS
bot.stock = StockSystem(bot.mem)
bot.ticket = TicketSystem(bot.brain)
bot.notify = NotifySystem(bot.brain, bot)

# 💾 BACKUP SYSTEM
bot.backup = BackupSystem(bot.brain, bot)

# 📊 STATUS SYSTEM
bot.status = StatusSystem(bot.mem)

# 🛒 ORDER SYSTEM (ต้องมี backup ด้วย)
bot.order = OrderSystem(
    bot.mem,
    bot.ticket,
    bot.notify,
    bot.backup
)

# 🔥 READY
@bot.event
async def on_ready():
    print("🟢 FULL SHOP SYSTEM ONLINE")

# 🎮 COMMAND UI
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    # 🛒 SHOP
    if message.content == "!shop":
        await message.channel.send("🛒 SHOP ONLINE", view=ShopView(bot))

    # 🛠 ADMIN PANEL
    if message.content == "!admin":
        await message.channel.send("🛠 ADMIN PANEL", view=AdminView(bot))

# 🚀 RUN BOT
bot.run(os.getenv("TOKEN"))
