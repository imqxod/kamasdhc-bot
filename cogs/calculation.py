import discord
from discord.ext import commands
from utils.config import *

gids = get_guild_ids()

class CalculationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="calculate", description="Calculate how much time it'll take to drop money", guild_ids=gids)
    async def calculatecmd(self, ctx: discord.ApplicationContext, alts: discord.Option(int, description="How many accounts are you using to drop"), cash: discord.Option(int, description="How much cash in millions are you dropping")):
        delay = 15
        drop_amount = 8500
        total_drops = (cash * 1_000_000) / drop_amount
        total_seconds = total_drops * delay
        total_seconds /= alts
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        embed = discord.Embed(title="Calculation", description="", color=discord.Colour.blue())
        embed.add_field(name="Accounts", value=f"{alts} accounts", inline=False)
        embed.add_field(name="Cash", value=f"{cash} million(s)", inline=False)
        embed.add_field(name="Hours", value=f"{int(hours)} hours", inline=False)
        embed.add_field(name="Minutes", value=f"{int(minutes)} minutes", inline=False)
        embed.add_field(name="Seconds", value=f"{int(seconds)} seconds", inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CalculationCog(bot))
