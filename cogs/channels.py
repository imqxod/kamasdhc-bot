import discord
from discord.ext import commands
from utils.config import *

gids = get_guild_ids()

class ChannelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="delchannel", description="Delete current channel", guild_ids=gids)
    async def delchannel(self, ctx: discord.ApplicationContext):
        channel = ctx.channel
        try:
            await channel.delete()
            embed = discord.Embed(
                title="Chanel Deleted",
                description=f"Ticket channel {channel.name} has been deleted.",
                color=discord.Color.green()
            )
            await ctx.respond(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="Delete Ticket Error",
                description="I do not have permission to delete this channel.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)
        except discord.HTTPException as e:
            embed = discord.Embed(
                title="Delete Ticket Error",
                description=f"Failed to delete channel: {e}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)

    @commands.slash_command(name="rename", description="Rename the current channel", guild_ids=gids)
    async def rename(self, ctx: discord.ApplicationContext, new_name: discord.Option(str, description="New channel name")):
        channel = ctx.channel
        try:
            await channel.edit(name=new_name)
            embed = discord.Embed(
                title="Channel Renamed",
                description=f"Channel has been renamed to {new_name}.",
                color=discord.Color.green()
            )
            await ctx.respond(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="Rename Channel Error",
                description="I do not have permission to rename this channel.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)
        except discord.HTTPException as e:
            embed = discord.Embed(
                title="Rename Channel Error",
                description=f"Failed to rename channel: {e}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(ChannelsCog(bot))