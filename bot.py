import discord
import os
from dotenv import load_dotenv

from shop import Shop
from ui import AdminPanel, StatusView

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot(intents=intents)

shop = Shop(bot)


@bot.event
async def on_ready():
    print("BOT READY")

    bot.loop.create_task(shop.live_dashboard())
    bot.loop.create_task(shop.stock_watcher())


@bot.command()
async def admin(ctx):
    await ctx.send("🧠 ADMIN PANEL", view=AdminPanel())


@bot.command()
async def shop(ctx):
    await ctx.send("🛒 ORDER PANEL", view=StatusView())


bot.run(os.getenv("DISCORD_TOKEN"))
