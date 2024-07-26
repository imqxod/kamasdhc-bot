import discord
from discord.ext import commands
from discord.commands import slash_command
from utils.embeds import read_embed
from utils.config import get_guild_ids, set_verify_channel

gids = get_guild_ids()

class CreateTicketModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Channel ID", custom_id="channel_id_input"))
        self.add_item(discord.ui.InputText(label="Color in RGB (r,g,b)", custom_id="color_input"))

    async def callback(self, interaction: discord.Interaction):
        channel_id = self.children[0].value
        channel = interaction.guild.get_channel(int(channel_id))

        result_embed = discord.Embed(title="Result")
        result_embed.add_field(name="Status", value="Creating embed...", inline=False)

        await interaction.response.send_message(embeds=[result_embed])

        if channel is not None:
            embed_data = read_embed('verification.json')
            if embed_data is None:
                result_embed.add_field(name="Status", value="Failed to read embed data", inline=False)
                await interaction.edit_original_response(embeds=[result_embed])
                return

            rgb = tuple(map(int, self.children[1].value.split(',')))
            color = (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]

            embed = discord.Embed(title=embed_data['title'], description=embed_data['description'], color=color)
            for name, value in embed_data['fields'].items():
                embed.add_field(name=name, value=value)

            verify_channel = interaction.guild.get_channel(channel_id)
            print(verify_channel)
            set_verify_channel(verify_channel.id)
            
            message = await verify_channel.send(embed=embed)
            await message.add_reaction(":white_check_mark:")

            result_embed.set_field_at(index=0, name="Status", value="Embed created, channel id set", inline=False)
            await interaction.edit_original_response(embeds=[result_embed])
        else:
            result_embed.add_field(name="Status", value="Channel not found", inline=False)
            await interaction.edit_original_response(embeds=[result_embed])

class VerificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='createverificationmessage', description='Create verification message', guild_ids=gids)
    async def ticketcreate(self, ctx: discord.ApplicationContext):
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(title="You do not have permissions to use this command!", description="", color=discord.Colour.red())
            await ctx.respond(embed=embed)
            return
        modal = CreateTicketModal(title='Create verification message')
        await ctx.send_modal(modal)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(1248681672199770183) # hardcoded role it due to config not working
        await payload.member.add_roles(role)

def setup(bot):
    bot.add_cog(VerificationCog(bot))
