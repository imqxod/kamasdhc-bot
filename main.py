import discord
import sys
import os
from utils.config import *
from utils.db_helper import *
from cogs import tickets 

sys.dont_write_bytecode = True

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    loaded_cogs = 0
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            loaded_cogs += 1

    await bot.sync_commands()
    bot.add_view(tickets.CreateTicketSelect())

    output = f"""
    KDHC Bot
    
    Loaded cogs: {loaded_cogs}"""

    print(output)

bot.run(get_token(), "kdhc-main")