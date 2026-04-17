import discord,os
from dotenv import load_dotenv

from database import Database
from stock import Stock
from price import Price
from notify import Notify
from status import Status
from backup import Backup
from ticket import Ticket
from dashboard import Dashboard
from security import Security

from engine import Engine
from admin_panel import AdminPanel
from order_modal import OrderModal

load_dotenv()

bot=discord.Client(intents=discord.Intents.all())

db=Database()
stock=Stock(db)
price=Price(db)
notify=Notify(bot)

status=Status(["ACCEPTED","FARMING","DELIVERING","DONE"])
backup=Backup()
dashboard=Dashboard(db)

ticket=Ticket({"DISCORD":{"CHANNELS":{"TICKET_CATEGORY":0}}})

engine=Engine(db,stock,notify,status)

bot.db=db
bot.engine=engine
bot.backup=backup
bot.dashboard=dashboard

@bot.event
async def on_ready():
    print("🟢 FULL SYSTEM ONLINE")

@bot.event
async def on_message(m):

    if m.author.bot:
        return

    if m.content=="!buy":
        await m.channel.send_modal(OrderModal())

    if m.content=="!admin":
        await m.channel.send("🧠 ADMIN PANEL",view=AdminPanel())

    if m.content=="!dashboard":
        await m.channel.send(embed=dashboard.build())

    if m.content=="!backup":
        backup.run()
        await m.channel.send("✔ BACKUP DONE")

bot.run(os.getenv("DISCORD_TOKEN"))
