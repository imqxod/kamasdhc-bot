import discord
from discord.ext import commands
from utils.config import *

gids = get_guild_ids()

class VouchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 1247552666079461480:
            if not message.author == self.bot.user:
                if "vouch" in message.content.lower():
                    await message.add_reaction("✅")

def setup(bot):
    bot.add_cog(VouchCog(bot))
