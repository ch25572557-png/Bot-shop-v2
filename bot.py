import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from shop import ShopSystem
from ticket import TicketSystem

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

shop = ShopSystem(bot)
ticket = TicketSystem(bot, shop)

@bot.event
async def on_ready():
    print(f"Bot Ready: {bot.user}")

@bot.command()
async def setup(ctx):
    await ticket.send_ticket_panel(ctx.channel)

bot.run(TOKEN)
