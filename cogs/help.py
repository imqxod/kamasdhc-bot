import discord
from discord.ext import commands
from utils.config import *

gids = get_guild_ids()

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="cogs", description="Display all loaded cogs", guild_ids=gids)
    async def cogs(self, ctx: discord.ApplicationContext):
        loaded_cogs = [cog for cog in self.bot.cogs.keys()]
        embed = discord.Embed(title="Loaded Cogs", description="\n".join(loaded_cogs), color=discord.Color.blue())
        await ctx.respond(embed=embed)

    @commands.slash_command(name="help", description="Get command help for a specific cog", guild_ids=gids)
    async def help(self, ctx: discord.ApplicationContext, cog: discord.Option(str, description="The name of the cog")):
        cog = self.bot.get_cog(cog)
        if cog is None:
            await ctx.respond("Cog not found.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Help for {cog.qualified_name} Cog", color=discord.Color.green())
        for command in cog.get_commands():
            embed.add_field(name=f"/{command.name}", value=command.description or "No description", inline=False)
        
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(HelpCog(bot))
