import discord
from discord.ext import commands
from discord.ui import Modal, InputText
from utils.db_helper import SQLiteDBHelper
from utils.config import *
import json

gids = get_guild_ids()

class FieldModal(Modal):
    def __init__(self, embed_id):
        super().__init__(title="Add Field to Embed")
        self.embed_id = embed_id
        self.add_item(InputText(label="Field Title", placeholder="Enter field title"))
        self.add_item(InputText(label="Field Value", placeholder="Enter field value"))

    async def callback(self, interaction: discord.Interaction):
        title = self.children[0].value
        value = self.children[1].value

        db_helper = SQLiteDBHelper("embeds.db")
        db_helper.create_connection()

        embed_data = db_helper.execute_read_query("SELECT fields FROM embeds WHERE id = ?", (self.embed_id,))
        if embed_data and embed_data[0][0]:
            try:
                fields = json.loads(embed_data[0][0])
            except json.JSONDecodeError:
                fields = []
        else:
            fields = []

        fields.append({"name": title, "value": value})

        db_helper.execute_query("UPDATE embeds SET fields = ? WHERE id = ?", (json.dumps(fields), self.embed_id))
        db_helper.close_connection()

        embed = discord.Embed(title="Embed Updated", description=f"Embed ID: {self.embed_id}")
        embed.add_field(name="Field Title", value=title)
        embed.add_field(name="Field Value", value=value)
        embed.color = discord.Color.green()

        await interaction.response.send_message(embed=embed)

class EmbedModal(Modal):
    def __init__(self):
        super().__init__(title="Create Embed")
        self.add_item(InputText(label="Title", placeholder="Enter embed title"))
        self.add_item(InputText(label="Description", placeholder="Enter embed description", style=discord.InputTextStyle.paragraph))
        self.add_item(InputText(label="Color (RGB)", placeholder="Enter RGB color code (comma-separated)"))

    async def callback(self, interaction: discord.Interaction):
        title = self.children[0].value
        description = self.children[1].value
        color_rgb = self.children[2].value

        db_helper = SQLiteDBHelper("embeds.db")
        db_helper.create_connection()

        db_helper.execute_query("INSERT INTO embeds (title, description, rgbcolor, fields) VALUES (?, ?, ?, ?)", (title, description, color_rgb, json.dumps([])))
        db_helper.close_connection()

        embed = discord.Embed(title="Embed Created", description=f"Embed: {title}")
        embed.add_field(name="Description", value=description)
        embed.color = discord.Color.from_rgb(*map(int, color_rgb.split(',')))

        await interaction.response.send_message(embed=embed)

class EmbedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def has_manage_messages(self, ctx):
        """Check if the user has manage_messages permission."""
        permissions = ctx.author.guild_permissions
        if permissions.manage_messages:
            return True
        else:
            embed = discord.Embed(title="Permission Denied", description="You do not have permission to manage messages.", color=discord.Color.red())
            await ctx.respond(embed=embed)
            return False

    @commands.slash_command(name="embedsend", description="Send an embed by ID", guild_ids=gids)
    async def embed_send(self, ctx: discord.ApplicationContext, embed_id: discord.Option(int, description="ID of the embed to send")):
        if not await self.has_manage_messages(ctx):
            return
    
        embed = await self.get_embed(embed_id)
        if embed:
            await ctx.send(embed=embed)
            embed_response = discord.Embed(title="Embed Sent", description=f"Embed ID: {embed_id}", color=discord.Color.green())
            await ctx.respond(embed=embed_response)
        else:
            embed_response = discord.Embed(title="Embed Not Found", description="The specified embed ID does not exist.", color=discord.Color.red())
            await ctx.respond(embed=embed_response)

    @commands.slash_command(name="embedaddfield", description="Add a field to an embed", guild_ids=gids)
    async def embed_addfield(self, ctx: discord.ApplicationContext, embed_id: discord.Option(int, description="ID of the embed to modify")):
        if not await self.has_manage_messages(ctx):
            return
        
        await ctx.send_modal(FieldModal(embed_id=embed_id))

    @commands.slash_command(name="embedsetauthor", description="Set author of an embed", guild_ids=gids)
    async def embed_setauthor(self, ctx: discord.ApplicationContext, embed_id: discord.Option(int, description="ID of the embed to modify"), author: str):
        if not await self.has_manage_messages(ctx):
            return

        await self.update_embed(embed_id, "author", author)
        embed_response = discord.Embed(title="Embed Updated", description=f"Set author for embed ID: {embed_id}", color=discord.Color.green())
        await ctx.respond(embed=embed_response)

    @commands.slash_command(name="embedsetfooter", description="Set footer of an embed", guild_ids=gids)
    async def embed_setfooter(self, ctx: discord.ApplicationContext, embed_id: discord.Option(int, description="ID of the embed to modify"), footer: str):
        if not await self.has_manage_messages(ctx):
            return

        await self.update_embed(embed_id, "footer", footer)
        embed_response = discord.Embed(title="Embed Updated", description=f"Set footer for embed ID: {embed_id}", color=discord.Color.green())
        await ctx.respond(embed=embed_response)

    @commands.slash_command(name="embedsetbigimage", description="Set big image URL of an embed", guild_ids=gids)
    async def embed_setbigimage(self, ctx: discord.ApplicationContext, embed_id: discord.Option(int, description="ID of the embed to modify"), big_image: str):
        if not await self.has_manage_messages(ctx):
            return

        await self.update_embed(embed_id, "big_image_url", big_image)
        embed_response = discord.Embed(title="Embed Updated", description=f"Set big image for embed ID: {embed_id}", color=discord.Color.green())
        await ctx.respond(embed=embed_response)

    @commands.slash_command(name="embedsetthumbnail", description="Set thumbnail URL of an embed", guild_ids=gids)
    async def embed_setthumbnail(self, ctx: discord.ApplicationContext, embed_id: discord.Option(int, description="ID of the embed to modify"), thumbnail: str):
        if not await self.has_manage_messages(ctx):
            return

        await self.update_embed(embed_id, "thumbnail_url", thumbnail)
        embed_response = discord.Embed(title="Embed Updated", description=f"Set thumbnail for embed ID: {embed_id}", color=discord.Color.green())
        await ctx.respond(embed=embed_response)

    @commands.slash_command(name="getembeds", description="Retrieve all embed IDs", guild_ids=gids)
    async def get_embeds(self, ctx: discord.ApplicationContext):
        db_helper = SQLiteDBHelper("embeds.db")
        db_helper.create_connection()
        embeds = db_helper.execute_read_query("SELECT id FROM embeds")
        db_helper.close_connection()

        if not embeds:
            embed_response = discord.Embed(title="No Embeds Found", description="No embeds found in the database.", color=discord.Color.red())
            await ctx.respond(embed=embed_response)
            return

        embed_ids = [str(embed[0]) for embed in embeds]
        embed_list = "\n".join(embed_ids)
        embed_response = discord.Embed(title="Embed IDs", description=embed_list, color=discord.Color.blue())
        await ctx.respond(embed=embed_response)

    @commands.slash_command(name="embedcreate", description="Create a new embed", guild_ids=gids)
    async def create_embed(self, ctx: discord.ApplicationContext):
        if not await self.has_manage_messages(ctx):
            return
        
        await ctx.send_modal(EmbedModal())

    @commands.slash_command(name="embeddelete", description="Delete an embed by ID", guild_ids=gids)
    async def delete_embed(self, ctx: discord.ApplicationContext, embed_id: discord.Option(int, description="ID of the embed to delete")):
        if not await self.has_manage_messages(ctx):
            return

        db_helper = SQLiteDBHelper("embeds.db")
        db_helper.create_connection()

        # Check if embed exists
        embed = db_helper.execute_read_query("SELECT * FROM embeds WHERE id = ?", (embed_id,))
        if not embed:
            db_helper.close_connection()
            embed_response = discord.Embed(title="Embed Not Found", description=f"No embed found with ID {embed_id}.", color=discord.Color.red())
            await ctx.respond(embed=embed_response)
            return

        # Delete embed
        db_helper.execute_query("DELETE FROM embeds WHERE id = ?", (embed_id,))
        db_helper.close_connection()

        embed_response = discord.Embed(title="Embed Deleted", description=f"Embed ID {embed_id} has been deleted.", color=discord.Color.green())
        await ctx.respond(embed=embed_response)

    async def get_embed(self, embed_id):
        db_helper = SQLiteDBHelper("embeds.db")
        db_helper.create_connection()
        embed_data = db_helper.execute_read_query("SELECT * FROM embeds WHERE id = ?", (embed_id,))
        db_helper.close_connection()

        if embed_data:
            try:
                fields = json.loads(embed_data[0][4])
            except json.JSONDecodeError:
                fields = []
            
            embed = discord.Embed(title=embed_data[0][1], description=embed_data[0][2], color=discord.Color.from_rgb(*map(int, embed_data[0][3].split(','))))
            embed.set_thumbnail(url=embed_data[0][6])
            embed.set_image(url=embed_data[0][5])
            if embed_data[0][7]:
                embed.set_author(name=embed_data[0][7])
            if embed_data[0][8]:
                embed.set_footer(text=embed_data[0][8])
            
            for field in fields:
                embed.add_field(name=field["name"], value=field["value"])
                
            return embed
        else:
            return None

    async def update_embed(self, embed_id, column, value):
        db_helper = SQLiteDBHelper("embeds.db")
        db_helper.create_connection()
        db_helper.execute_query(f"UPDATE embeds SET {column} = ? WHERE id = ?", (value, embed_id))
        db_helper.close_connection()

def setup(bot):
    bot.add_cog(EmbedCog(bot))
