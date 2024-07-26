import discord
from discord.ext import commands
from discord.commands import slash_command
from utils.config import get_guild_ids

gids = get_guild_ids()

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="ban", description="Ban someone", guild_ids=gids)
    async def ban(self, ctx: discord.ApplicationContext, 
                  member: discord.Option(discord.User, description="Who do you want to ban?"), 
                  reason: discord.Option(str, description="Reason for the ban")):
        if not ctx.user.guild_permissions.ban_members:
            no_perm_embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to ban members.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=no_perm_embed, ephemeral=True)
            return
         
        embed = discord.Embed(
            title="You have been banned",
            description=f"Reason: {reason}",
            color=discord.Color.red()
        )

        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            dm_fail_embed = discord.Embed(
                title="Failed to send DM",
                description="They might have DMs disabled.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=dm_fail_embed, ephemeral=True)

        await ctx.guild.ban(member, reason=reason)

        success_embed = discord.Embed(
            title="Member Banned",
            description=f"{member.mention} has been banned for: {reason}",
            color=discord.Color.green()
        )
        await ctx.respond(embed=success_embed, ephemeral=True)

    @slash_command(name="kick", description="Kick someone", guild_ids=gids)
    async def kick(self, ctx: discord.ApplicationContext, 
                   member: discord.Option(discord.Member, description="Who do you want to kick?"), 
                   reason: discord.Option(str, description="Reason for the kick")):
        if not ctx.author.guild_permissions.kick_members:
            no_perm_embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to kick members.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=no_perm_embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="You have been kicked",
            description=f"Reason: {reason}",
            color=discord.Color.red()
        )

        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            failed_dm_embed = discord.Embed(
                title="Failed to send DM",
                description="They might have DMs disabled.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=failed_dm_embed, ephemeral=True)
        
        await ctx.guild.kick(member, reason=reason)

        confirm_embed = discord.Embed(
            title="Member Kicked",
            description=f"{member.mention} has been kicked for: {reason}",
            color=discord.Color.green()
        )
        await ctx.respond(embed=confirm_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(ModerationCog(bot))
