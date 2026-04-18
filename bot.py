import discord
import os
from discord.ext import commands

from brain import Brain
from memory import Memory

from ticket import TicketSystem
from stock import StockSystem
from notify import NotifySystem
from order import OrderSystem
from backup import BackupSystem

from shop import ShopView
from admin import AdminView

# 🔥 INTENTS
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# 🧠 CORE
bot.brain = Brain()
bot.mem = Memory()

# 📦 SYSTEMS
bot.stock = StockSystem(bot.mem)
bot.ticket = TicketSystem(bot.brain, bot)   # ✔ แก้
bot.notify = NotifySystem(bot.brain, bot)
bot.backup = BackupSystem(bot.brain, bot)

# 🛒 ORDER
bot.order = OrderSystem(
    bot.mem,
    bot.ticket,
    bot.notify,
    bot.backup,
    bot.brain   # ✔ เพิ่ม
)

# =====================
# 🚀 READY
# =====================
@bot.event
async def on_ready():
    print("🟢 FULL SHOP SYSTEM ONLINE")

# =====================
# 💬 COMMANDS
# =====================

@bot.command()
async def shop(ctx):
    await ctx.send("🛒 SHOP ONLINE", view=ShopView(bot))

@bot.command()
async def admin(ctx):
    await ctx.send("🛠 ADMIN PANEL", view=AdminView(bot))

# =====================
# 🚀 RUN
# =====================
bot.run(os.getenv("DISCORD_TOKEN"))
