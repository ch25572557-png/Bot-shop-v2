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

# =====================
# 🔥 INTENTS
# =====================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# =====================
# 🧠 CORE
# =====================
bot.brain = Brain()
bot.mem = Memory()

# =====================
# 📦 SYSTEMS
# =====================
bot.stock = StockSystem(bot.mem)

# ✔ FIX: TicketSystem ต้องรับ (brain, bot)
bot.ticket = TicketSystem(bot.brain, bot)

bot.notify = NotifySystem(bot.brain, bot)
bot.backup = BackupSystem(bot.brain, bot)

# =====================
# 🛒 ORDER SYSTEM
# =====================
bot.order = OrderSystem(
    bot.mem,
    bot.ticket,
    bot.notify,
    bot.backup,
    bot.brain
)

# =====================
# 🚀 READY
# =====================
@bot.event
async def on_ready():

    print("🟢 FULL SHOP SYSTEM ONLINE")

    # 🔥 persistent UI (สำคัญมาก)
    try:
        bot.add_view(ShopView(bot))
        bot.add_view(AdminView(bot))
    except Exception as e:
        print("[VIEW REGISTER ERROR]", e)


# =====================
# 💬 COMMANDS
# =====================
@bot.command()
async def shop(ctx):
    try:
        await ctx.send("🛒 SHOP ONLINE", view=ShopView(bot))
    except Exception as e:
        print("[SHOP CMD ERROR]", e)


@bot.command()
async def admin(ctx):
    try:
        await ctx.send("🛠 ADMIN PANEL", view=AdminView(bot))
    except Exception as e:
        print("[ADMIN CMD ERROR]", e)


# =====================
# 🚀 SAFE RUN
# =====================
token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ Missing DISCORD_TOKEN")
else:
    bot.run(token)
