import discord
from discord.ext import commands
from discord.commands import slash_command
from utils.embeds import read_embed
from utils.config import get_guild_ids, get_ticket_count, set_ticket_count, get_ticketmanager_role, get_dropper_role

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
            embed_data = read_embed('buydhc.json')
            if embed_data is None:
                result_embed.add_field(name="Status", value="Failed to read embed data", inline=False)
                await interaction.edit_original_response(embeds=[result_embed])
                return

            rgb = tuple(map(int, self.children[1].value.split(',')))
            color = (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]

            embed = discord.Embed(title=embed_data['title'], description=embed_data['description'], color=color)
            for name, value in embed_data['fields'].items():
                embed.add_field(name=name, value=value)

            await channel.send(embed=embed, view=CreateTicketSelect())

            result_embed.set_field_at(index=0, name="Status", value="Embed created", inline=False)
            await interaction.edit_original_response(embeds=[result_embed])
        else:
            result_embed.add_field(name="Status", value="Channel not found", inline=False)
            await interaction.edit_original_response(embeds=[result_embed])

def get_ticket_count_and_increment():
    count = get_ticket_count()
    set_ticket_count(int(count) + 1)
    return int(count) + 1

def get_ticket_name():
    return "ticket-" + str(get_ticket_count())

#region ticket management
class TicketManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(DeleteButton())

class DeleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Delete ticket", row=0, style=discord.ButtonStyle.danger, emoji="❌", custom_id="delete_ticket_button")

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(title="You do not have permissions to use this command!", description="", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(title="Delete ticket", description="Are you sure you want to delete this ticket?", color=discord.Colour.red())
        await interaction.response.send_message(embed=embed, view=DeleteView())

class DeleteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ConfirmDeleteButton())

class ConfirmDeleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Delete ticket", row=0, style=discord.ButtonStyle.danger, emoji="❌", custom_id="confirm_delete_button")

    async def callback(self, interaction: discord.Interaction):
        await interaction.channel.delete()
#endregion ticket management


class CreateTicketSelect(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="create_ticket_select",
        placeholder="Choose the payment method",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Paypal FNF",
                description="Pick this to pay with Paypal FNF"
            ),
            discord.SelectOption(
                label="Robux",
                description="Pick this to pay with robux"
            ),
            discord.SelectOption(
                label="Skins",
                description="Pick this to pay with da hood skins"
            )
        ]
    )
    async def select_callback(self, select, interaction):
        ticket_name = f"ticket-{get_ticket_count_and_increment()}"
        ticket_manager_role_id = get_ticketmanager_role()
        ticket_manager_role = interaction.guild.get_role(int(ticket_manager_role_id))
        dropper_role_id = get_dropper_role()
        dropper_role = interaction.guild.get_role(int(dropper_role_id))
        overwrites = {
            interaction.user: discord.PermissionOverwrite(view_channel=True),
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ticket_manager_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            dropper_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        channel = await interaction.guild.create_text_channel(name=ticket_name, overwrites=overwrites)
        if select.values[0] == "Robux":
            channelembed = discord.Embed(
            title='Hi',
            description="https://www.roblox.com/games/17741135713/KDHC",
            color=discord.Colour.blue()
        )
        elif select.values[0] == "Paypal FNF":
            channelembed = discord.Embed(
            title='Hi',
            description="https://paypal.me/ownerofkdhc",
            color=discord.Colour.blue()
        )
        elif select.values[0] == "Skins":
            channelembed = discord.Embed(
            title='Hi',
            description="https://www.roblox.com/users/4773757991/profile",
            color=discord.Colour.blue()
        )
        channelembed.add_field(name="Ticket type", value="Buy DHC", inline=False)
        channelembed.add_field(name="Payment method", value=f"{select.values[0]}", inline=False)
        channelembed.add_field(name="Member", value=f"{interaction.user.name}", inline=False)
        await channel.send(embed=channelembed, view=TicketManagementView())
        embed = discord.Embed(title='Ticket created!', description=f'Ticket channel: #{ticket_name}', color=discord.Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='createticketpanel', description='Create ticket panel for buying DHC', guild_ids=gids)
    async def ticketcreate(self, ctx: discord.ApplicationContext):
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(title="You do not have permissions to use this command!", description="", color=discord.Colour.red())
            await ctx.respond(embed=embed)
            return
        modal = CreateTicketModal(title='Create ticket panel')
        await ctx.send_modal(modal)

def setup(bot):
    bot.add_cog(TicketsCog(bot))
