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
from cancel_view import CancelView
from admin_dashboard import AdminDashboard
from stock_view import StockView

from stock_alert import StockAlertSystem
from dashboard_worker import DashboardWorker

# ✅ เพิ่ม
from status_view import StatusView
from farm_manager import FarmManager


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
bot.stock = StockSystem(bot.mem, bot.brain, bot, None)

bot.ticket = TicketSystem(bot.brain, bot)
bot.notify = NotifySystem(bot.brain, bot)
bot.backup = BackupSystem(bot.brain, bot)

# inject notify
bot.stock.notify = bot.notify

bot.order = OrderSystem(
    bot.mem,
    bot.ticket,
    bot.notify,
    bot.backup,
    bot.brain,
    bot
)

# 🔥 NEW: farm manager
bot.farm = FarmManager(bot.mem, bot.brain, bot.order)
bot.order.farm_manager = bot.farm

bot.stock_alert = StockAlertSystem(bot)
bot.dashboard = DashboardWorker(bot)


# =====================
# 🚀 READY EVENT
# =====================
@bot.event
async def on_ready():

    if getattr(bot, "ready_done", False):
        return
    bot.ready_done = True

    print(f"🟢 LOGGED IN AS {bot.user}")

    # =====================
    # 🧠 MEMORY INIT
    # =====================
    try:
        await bot.mem.init()
        print("🧠 MEMORY INIT DONE")
    except Exception as e:
        print("[MEM INIT ERROR]", e)

    # =====================
    # 🎛 VIEWS (🔥 FIX สำคัญ)
    # =====================
    try:
        bot.add_view(ShopView(bot))
        bot.add_view(AdminView(bot))
        bot.add_view(CancelView(bot))
        bot.add_view(StockView(bot))
        bot.add_view(AdminDashboard(bot))

        # 🔥 สำคัญสุด: ทำให้ปุ่ม ticket ไม่หาย
        bot.add_view(StatusView(bot, 0))

        print("🎛 VIEWS REGISTERED")
    except Exception as e:
        print("[VIEW ERROR]", e)

    # =====================
    # 🚀 START SYSTEMS
    # =====================
    async def run(fn):
        try:
            result = fn()
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            print("[SYSTEM ERROR]", e)

    await run(bot.stock.start)
    await run(bot.order.start)
    await run(bot.farm.start)          # 🔥 NEW
    await run(bot.stock_alert.start)
    await run(bot.dashboard.start)

    print("🚀 ALL SYSTEMS STARTED")


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
if __name__ == "__main__":

    token = os.getenv("DISCORD_TOKEN")

    if not token:
        print("❌ Missing DISCORD_TOKEN")
    else:
        bot.run(token)
