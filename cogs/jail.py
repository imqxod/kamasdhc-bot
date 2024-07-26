import discord
from discord.ext import commands
import json
from utils.config import is_administrator_role, get_jailed_role, get_guild_ids
from utils.db_helper import SQLiteDBHelper
import os

gids = get_guild_ids()

class JailCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = os.path.join(os.path.dirname(__file__), "../", "jail_roles.db")
        self.db_helper = SQLiteDBHelper(self.db_file)
        self.db_helper.create_connection()
        self.create_roles_table()

    def create_roles_table(self):
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INTEGER PRIMARY KEY,
                role_ids TEXT
            );
        """
        self.db_helper.create_table(create_table_sql)

    async def can_jail(self, ctx, member):
        if is_administrator_role(member.id):
            await ctx.send("You cannot jail this member.")
            return False

        jail_role_id = get_jailed_role()
        jail_role = ctx.guild.get_role(int(jail_role_id))

        if not jail_role:
            await ctx.send("Jail role not found. Please configure the jail role ID correctly in the config.")
            return False

        return jail_role
    
    async def cog_check(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You do not have permission to jail people.")
            return False
        return True

    @commands.slash_command(
        name="jail",
        description="Jails a member.",
        guild_ids=gids
    )
    async def jail_member(self, ctx, member: discord.Member, *, reason):
        if not await self.cog_check(ctx):
            return
        jail_role = await self.can_jail(ctx, member)
        if not jail_role:
            return

        # Store the user's current roles except roles that cannot be removed
        roles = [role for role in member.roles if role != ctx.guild.default_role and not role.is_premium_subscriber()]
        roles_json = json.dumps([role.id for role in roles])
        sql = "INSERT OR REPLACE INTO user_roles (user_id, role_ids) VALUES (?, ?);"
        self.db_helper.execute_query(sql, (member.id, roles_json))

        # Debug: Log roles
        print(f"Member roles before jailing: {roles}")

        # Remove all roles except the jail role
        try:
            for role in roles:
                try:
                    await member.remove_roles(role, reason=f"Jailed by {ctx.author} for: {reason}")
                except discord.Forbidden:
                    print(f"Failed to remove role: {role.name} ({role.id})")
            await member.add_roles(jail_role, reason=f"Jailed by {ctx.author} for: {reason}")
        except discord.Forbidden as e:
            print(f"Error: {e}")
            return await ctx.respond(f"I don't have permission to manage roles.")

        # Inform the user
        await ctx.respond(f"{member.mention} has been jailed for: {reason}")

        # Send embed to member's DMs
        embed = discord.Embed(
            title="You have been jailed",
            description=f"Reason: {reason}\n",
            color=discord.Color.red()
        )

        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass  # Ignore if unable to send DM

    @commands.slash_command(
        name="unjail",
        description="Unjails a member.",
        guild_ids=gids
    )
    async def unjail_member(self, ctx, member: discord.Member):
        if not await self.cog_check(ctx):
            return
        jail_role = await self.can_jail(ctx, member)
        if not jail_role:
            return

        # Retrieve stored roles from the database
        sql = "SELECT role_ids FROM user_roles WHERE user_id = ?;"
        result = self.db_helper.execute_read_query(sql, (member.id,))
        if not result:
            return await ctx.send(f"{member.mention} does not have any stored roles to restore.")

        role_ids = json.loads(result[0][0])
        roles = [ctx.guild.get_role(role_id) for role_id in role_ids]

        # Debug: Log roles to be restored
        print(f"Restoring roles to member: {role_ids}")

        # Remove the jail role and add back the stored roles
        try:
            await member.remove_roles(jail_role, reason=f"Unjailed by {ctx.author}")
            for role in roles:
                if role:
                    try:
                        await member.add_roles(role, reason=f"Unjailed by {ctx.author}")
                    except discord.Forbidden:
                        print(f"Failed to add role: {role.name} ({role.id})")
            await ctx.respond(f"{member.mention} has been unjailed.")
        except discord.Forbidden as e:
            print(f"Error: {e}")
            await ctx.respond("I don't have permission to manage roles")

def setup(bot):
    bot.add_cog(JailCog(bot))
