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

# 🆕 CANCEL SYSTEM
from cancel_view import CancelView


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
bot.stock = StockSystem(bot.mem, bot)
bot.ticket = TicketSystem(bot.brain, bot)
bot.notify = NotifySystem(bot.brain, bot)
bot.backup = BackupSystem(bot.brain, bot)

bot.order = OrderSystem(
    bot.mem,
    bot.ticket,
    bot.notify,
    bot.backup,
    bot.brain,
    bot
)

# =====================
# 🚀 READY EVENT
# =====================
@bot.event
async def on_ready():
    print(f"🟢 LOGGED IN AS {bot.user}")

    if getattr(bot, "ready_done", False):
        return
    bot.ready_done = True

    # =====================
    # 🎛 REGISTER VIEWS
    # =====================
    try:
        bot.add_view(ShopView(bot))
        bot.add_view(AdminView(bot))
        bot.add_view(CancelView(bot))  # ✅ FIXED

        print("✅ VIEWS REGISTERED")

    except Exception as e:
        print("[VIEW REGISTER ERROR]", e)

    # =====================
    # 📦 STOCK START
    # =====================
    try:
        if hasattr(bot.stock, "start") and callable(bot.stock.start):
            bot.stock.start()
            print("📦 STOCK SYSTEM STARTED")
    except Exception as e:
        print("[STOCK START ERROR]", e)

    # =====================
    # 🛒 ORDER START
    # =====================
    try:
        if hasattr(bot.order, "start"):
            result = bot.order.start()
            if hasattr(result, "__await__"):
                await result

            print("🛒 ORDER SYSTEM STARTED")

    except Exception as e:
        print("[ORDER START ERROR]", e)

# =====================
# 💬 COMMANDS
# =====================
@bot.command()
async def shop(ctx):
    embed = discord.Embed(
        title="🛒 SHOP ONLINE",
        description="เลือกสินค้าด้านล่าง",
        color=0x00ffcc
    )
    await ctx.send(embed=embed, view=ShopView(bot))


@bot.command()
async def admin(ctx):
    embed = discord.Embed(
        title="🛠 ADMIN PANEL",
        description="ระบบแอดมิน",
        color=0xffcc00
    )
    await ctx.send(embed=embed, view=AdminView(bot))


# =====================
# 🚀 RUN BOT
# =====================
token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ Missing DISCORD_TOKEN")
else:
    bot.run(token)
