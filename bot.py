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

bot.stock_alert = StockAlertSystem(bot)
bot.dashboard = DashboardWorker(bot)


# =====================
# 🚀 READY EVENT (V2 FIXED)
# =====================
@bot.event
async def on_ready():

    print(f"🟢 LOGGED IN AS {bot.user}")

    if getattr(bot, "ready_done", False):
        return
    bot.ready_done = True

    # =====================
    # 🧠 INIT MEMORY V2 (IMPORTANT FIX)
    # =====================
    try:
        await bot.mem.init()
        print("🧠 MEMORY INIT DONE")
    except Exception as e:
        print("[MEM INIT ERROR]", e)

    # =====================
    # 🎛 SAFE VIEW REGISTER
    # =====================
    def safe_add(view_cls, name):
        try:
            bot.add_view(view_cls(bot))
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name} ERROR:", e)

    safe_add(ShopView, "ShopView")
    safe_add(AdminView, "AdminView")
    safe_add(CancelView, "CancelView")
    safe_add(StockView, "StockView")
    safe_add(AdminDashboard, "AdminDashboard")

    # =====================
    # 🚀 SAFE START SYSTEMS
    # =====================
    async def safe_start(name, fn):
        try:
            result = fn()

            if asyncio.iscoroutine(result):
                await result

            print(f"🚀 {name} STARTED")

        except Exception as e:
            print(f"[{name} ERROR]", e)

    await safe_start("STOCK", bot.stock.start)
    await safe_start("ORDER", bot.order.start)
    await safe_start("ALERT", bot.stock_alert.start)
    await safe_start("DASHBOARD", bot.dashboard.start)


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
async def main():

    token = os.getenv("DISCORD_TOKEN")

    if not token:
        print("❌ Missing DISCORD_TOKEN")
        return

    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
