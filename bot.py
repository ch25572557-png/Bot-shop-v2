import discord
import os
import asyncio
from dotenv import load_dotenv

from core.db import DB
from core.config import Config
from core.shop import Shop
from core.points import Points
from core.backup import Backup
from core.auto_backup import AutoBackup
from core.auto_restore import AutoRestore

from modules.product import Product
from modules.stock import Stock
from modules.dashboard import Dashboard
from modules.ticket import Ticket

from ui.ticket_ui import TicketButton
from systems.modal import OrderModal

load_dotenv()

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

bot.config = Config()
bot.db = DB()

bot.points = Points(bot.db)
bot.shop = Shop(bot.db, bot.points)

bot.product = Product(bot.db)
bot.stock = Stock(bot.db)
bot.dashboard = Dashboard()

bot.backup = Backup()
bot.auto_backup = AutoBackup(bot, 3600)
bot.auto_restore = AutoRestore(bot)

@bot.event
async def on_ready():
    print("🟢 SYSTEM READY")

    await bot.auto_restore.check_and_restore()

    ch = bot.get_channel(int(bot.config.get("CHANNELS.DASHBOARD")))
    if ch:
        await ch.send("🎫 SHOP ONLINE", view=TicketButton(bot))

    asyncio.create_task(bot.auto_backup.start())

@bot.event
async def on_message(m):
    if m.author.bot:
        return

    if m.content.startswith("!add"):
        _, n, p, s = m.content.split()
        bot.product.add(n, int(p), int(s))
        await m.channel.send("✔ ADDED")

    if m.content.startswith("!points"):
        p = bot.points.get(m.author.id)
        await m.channel.send(f"🎯 {p}")

    if m.content.startswith("!backup"):
        f = bot.backup.backup_db()
        await m.channel.send(f"💾 {f}")

bot.run(os.getenv("DISCORD_TOKEN"))
