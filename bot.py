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

from cancel_view import CancelView
from admin_dashboard import AdminDashboard
from stock_view import StockView


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
    # 🎛 SAFE VIEW REGISTER (FIXED)
    # =====================
    def safe_add(view_cls, name):
        try:
            bot.add_view(view_cls(bot))
            print(f"✅ {name} REGISTERED")
        except Exception as e:
            print(f"❌ {name} ERROR:", e)

    safe_add(ShopView, "ShopView")
    safe_add(AdminView, "AdminView")
    safe_add(CancelView, "CancelView")
    safe_add(StockView, "StockView")
    safe_add(AdminDashboard, "AdminDashboard")


    # =====================
    # 📦 STOCK START
    # =====================
    try:
        if hasattr(bot.stock, "start"):
            result = bot.stock.start()
            if hasattr(result, "__await__"):
                await result
        print("📦 STOCK STARTED")
    except Exception as e:
        print("[STOCK ERROR]", e)


    # =====================
    # 🛒 ORDER START
    # =====================
    try:
        if hasattr(bot.order, "start"):
            result = bot.order.start()
            if hasattr(result, "__await__"):
                await result
        print("🛒 ORDER STARTED")
    except Exception as e:
        print("[ORDER ERROR]", e)


# =====================
# 💬 COMMANDS
# =====================
@bot.command()
async def shop(ctx):
    await ctx.send(
        embed=discord.Embed(
            title="🛒 SHOP ONLINE",
            description="เลือกสินค้าด้านล่าง",
            color=0x00ffcc
        ),
        view=ShopView(bot)
    )


@bot.command()
async def admin(ctx):
    await ctx.send(
        embed=discord.Embed(
            title="🛠 ADMIN PANEL",
            color=0xffcc00
        ),
        view=AdminView(bot)
    )


@bot.command()
async def dashboard(ctx):
    await ctx.send(
        embed=discord.Embed(
            title="🧠 DASHBOARD",
            description="จัดการระบบทั้งหมด",
            color=0x2ecc71
        ),
        view=AdminDashboard(bot)
    )


# =====================
# 🚀 RUN BOT
# =====================
token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ Missing DISCORD_TOKEN")
else:
    bot.run(token)
