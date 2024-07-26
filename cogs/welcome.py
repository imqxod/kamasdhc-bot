import discord
from discord.ext import commands

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(title=f"{member.mention} drifted in kazuka", color=discord.Colour.blurple())
        embed.set_author(name=member.name, icon_url=member.avatar.url)
        embed.set_image(url="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3dmcWN2YjhhODJ2NDc4N2FmaHVkMTlvOXN3em5sb2s4Z2x1MW8zZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1ZquGCBEg1hr2jMk3D/giphy.gif")
        
        channel = member.guild.get_channel(1246789639101087855)
        print(channel)
        print(member.guild.name)
        if channel:
            await channel.send(embed=embed)
        else:
            print("[welcome.py] channel not found")

def setup(bot):
    bot.add_cog(WelcomeCog(bot))