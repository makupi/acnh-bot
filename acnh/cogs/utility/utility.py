import time
from datetime import datetime

import discord
from discord.ext import commands

from acnh.utils import create_embed


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now().replace(microsecond=0)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{type(self).__name__} Cog ready.')

    @commands.command()
    async def ping(self, ctx):
        embed = await create_embed()
        before_time = time.time()
        msg = await ctx.send(embed=embed)
        latency = round(self.bot.latency * 1000)
        elapsed_ms = round((time.time() - before_time) * 1000) - latency
        embed.add_field(name='ping', value=f'{elapsed_ms}ms')
        embed.add_field(name='latency', value=f'{latency}ms')
        await msg.edit(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        current_time = datetime.now().replace(microsecond=0)
        embed = await create_embed(description=f"Time since I went online: {current_time - self.start_time}.")
        await ctx.send(embed=embed)

    @commands.command()
    async def starttime(self, ctx):
        embed = await create_embed(description=f"I'm up since {self.start_time}.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
