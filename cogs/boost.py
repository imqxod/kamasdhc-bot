import discord
from discord.ext import commands
from utils.config import *

class BoostCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.type == discord.MessageType.premium_guild_subscription:
            await message.author.send("Thank you for boosting, please create a ticket to claim your DHC :dhcrgb:")
            await self.bot.get_channel(1247625514265350175).send(f"@everyone {message.author} boosted the server!")

def setup(bot):
    bot.add_cog(BoostCog(bot))
