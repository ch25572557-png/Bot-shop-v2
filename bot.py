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

# =====================
# 🔥 INTENTS
# =====================
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
    bot.brain,
    bot
)

# =====================
# 🚀 READY
# =====================
@bot.event
async def on_ready():

    print(f"🟢 LOGGED IN AS {bot.user}")

    # =====================
    # 🎛 VIEW REGISTER SAFE
    # =====================
    try:
        bot.add_view(ShopView(bot))
        bot.add_view(AdminView(bot))
    except Exception as e:
        print("[VIEW REGISTER ERROR]", e)

    # =====================
    # 🧠 FARM START SAFE (FIXED)
    # =====================
    if not getattr(bot, "farm_started", False):

        bot.farm_started = True

        try:
            await bot.order.start()
            print("🧠 FARM WORKER STARTED")
        except Exception as e:
            print("[FARM START ERROR]", e)

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
# 🚀 RUN BOT
# =====================
token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ Missing DISCORD_TOKEN")
else:
    bot.run(token)
