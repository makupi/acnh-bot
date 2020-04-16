import discord
from discord.ext import commands

from acnh.database.models import Guild
from acnh.utils import create_embed


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{type(self).__name__} Cog ready.')

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def prefix(self, ctx, new_prefix: str):
        embed = discord.Embed(description='Prefix changed')
        guild = await Guild.get(ctx.guild.id)
        if guild is None:
            await Guild.create(id=ctx.guild.id, prefix=new_prefix)
            self.bot.guild_data[ctx.guild.id] = {
                "prefix": new_prefix
            }
        else:
            embed.add_field(name='From', value=guild.prefix)
            await guild.update(prefix=new_prefix).apply()
            self.bot.guild_data[ctx.guild.id].update({"prefix": new_prefix})

        embed.add_field(name='To', value=new_prefix)
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Settings(bot))
