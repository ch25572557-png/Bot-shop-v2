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

# ⚠️ ถ้ามีไฟล์ view เพิ่ม ให้ import เพิ่มตรงนี้
# from ui import CancelView
# from ticket_view import TicketView

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

    # กันรันซ้ำ
    if getattr(bot, "ready_done", False):
        return
    bot.ready_done = True

    # =====================
    # 🎛 REGISTER VIEWS (สำคัญมาก)
    # =====================
    try:
        bot.add_view(ShopView(bot))
        bot.add_view(AdminView(bot))

        # ⚠️ เพิ่มถ้ามี
        # bot.add_view(CancelView())
        # bot.add_view(TicketView())

        print("✅ VIEWS REGISTERED")
    except Exception as e:
        print("[VIEW REGISTER ERROR]", e)

    # =====================
    # 📦 START STOCK SYSTEM
    # =====================
    try:
        if hasattr(bot.stock, "start"):
            bot.stock.start()
            print("📦 STOCK SYSTEM STARTED")
    except Exception as e:
        print("[STOCK START ERROR]", e)

    # =====================
    # 🧠 START ORDER SYSTEM
    # =====================
    try:
        if hasattr(bot.order, "start"):
            bot.order.start()
            print("🛒 ORDER SYSTEM STARTED")
    except Exception as e:
        print("[ORDER START ERROR]", e)

# =====================
# 💬 COMMANDS
# =====================
@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="🛒 SHOP ONLINE", color=0x00ffcc)
    await ctx.send(embed=embed, view=ShopView(bot))

@bot.command()
async def admin(ctx):
    embed = discord.Embed(title="🛠 ADMIN PANEL", color=0xffcc00)
    await ctx.send(embed=embed, view=AdminView(bot))

# =====================
# 🚀 RUN BOT
# =====================
token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ Missing DISCORD_TOKEN")
else:
    bot.run(token)
