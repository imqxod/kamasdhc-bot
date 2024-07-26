import discord
from discord.ext import commands
from utils.db_helper import SQLiteDBHelper
from utils.config import *
import os

gids = get_guild_ids()

class StickyMessageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = os.path.join(os.path.dirname(__file__), "../", "stickymessages.db")
        self.db_helper = SQLiteDBHelper(self.db_file)
        self.db_helper.create_connection()
        self.create_stickymessage_table()

    def create_stickymessage_table(self):
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS stickymessages (
                channel_id INTEGER PRIMARY KEY,
                content TEXT
            );
        """
        self.db_helper.execute_query(create_table_sql)

    async def cog_check(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You do not have permission to manage sticky messages.")
            return False
        return True

    @commands.slash_command(name="stickymessageadd", description="Add a sticky message to the channel", guild_ids=gids)
    async def add_sticky(self, ctx, *, content: str):
        await ctx.defer()  # Defer the response to avoid timeout
        if not await self.cog_check(ctx):
            await ctx.send("You do not have permission to manage sticky messages.")
            return
        channel_id = ctx.channel.id
        sql = "INSERT OR REPLACE INTO stickymessages (channel_id, content) VALUES (?, ?);"
        self.db_helper.execute_query(sql, (channel_id, content))

        embed = discord.Embed(title="Sticky message added", description=content, color=discord.Color.green())
        await ctx.respond(embed=embed)

    async def delete_previous_bot_messages(self, channel, sticky_content):
        async for message in channel.history(limit=100):  # Limit to a reasonable number to avoid performance issues
            if message.author == self.bot.user:
                if sticky_content in str(message.content):
                    await message.delete()
                    return

    @commands.slash_command(name="stickymessageremove", description="Remove the sticky message from the channel", guild_ids=gids)
    async def remove_sticky(self, ctx):
        await ctx.defer()  # Defer the response to avoid timeout
        if not await self.cog_check(ctx):
            await ctx.send("You do not have permission to manage sticky messages.")
            return
        channel_id = ctx.channel.id
        sql = "DELETE FROM stickymessages WHERE channel_id = ?;"
        self.db_helper.execute_query(sql, (channel_id,))
        
        embed = discord.Embed(title="Sticky message removed", color=discord.Color.red())
        await ctx.respond(embed=embed)

    @commands.slash_command(name="stickymessageedit", description="Edit the sticky message content for the channel", guild_ids=gids)
    async def edit_sticky(self, ctx, *, content: str):
        await ctx.defer()  # Defer the response to avoid timeout
        if not await self.cog_check(ctx):
            await ctx.send("You do not have permission to manage sticky messages.")
            return
        channel_id = ctx.channel.id
        sql = "UPDATE stickymessages SET content = ? WHERE channel_id = ?;"
        self.db_helper.execute_query(sql, (content, channel_id))

        embed = discord.Embed(title="Sticky message edited", description=content, color=discord.Color.blue())
        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        channel_id = message.channel.id
        sql = "SELECT content FROM stickymessages WHERE channel_id = ?;"
        result = self.db_helper.execute_read_query(sql, (channel_id,))
        
        if result:
            sticky_content = result[0][0]
            await self.delete_previous_bot_messages(message.channel, sticky_content)
            await message.channel.send(sticky_content)

    def cog_unload(self):
        self.db_helper.close_connection()
        print("Database connection closed.")

def setup(bot):
    bot.add_cog(StickyMessageCog(bot))
