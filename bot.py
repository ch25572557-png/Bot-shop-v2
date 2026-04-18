import discord
import os
import asyncio
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

intents = discord.Intents.all()
intents.message_content = True

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
# 🚀 READY (FIXED)
# =====================
@bot.event
async def on_ready():
    print(f"🟢 LOGGED IN AS {bot.user}")

    try:
        bot.add_view(ShopView(bot))
        bot.add_view(AdminView(bot))
    except Exception as e:
        print("[VIEW REGISTER ERROR]", e)

    # 🔥 FIX: START FARM WORKER AFTER LOOP READY
    if not hasattr(bot, "farm_started"):
        bot.farm_started = True
        bot.loop.create_task(bot.order.farm_worker())
        print("🧠 FARM WORKER STARTED")


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
# 🚀 SAFE RUN
# =====================
token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ Missing DISCORD_TOKEN")
else:
    bot.run(token)
