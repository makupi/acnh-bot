import discord
from discord.ext import commands
from acnh.database.models import Turnip


async def check_already_listed(user_id):
    t = await Turnip.get(user_id=user_id)
    if t is None:
        return False
    return True


class Turnips(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{type(self).__name__} Cog ready.')

    @commands.group(invoke_without_command=False, pass_context=True)
    async def turnip(self, ctx):
        pass

    @turnip.command()
    async def info(self, ctx):
        pass

    @turnip.command()
    async def list(self, ctx):
        await ctx.send('list')

    @turnip.command()
    async def sell(self, ctx, price, code):
        await ctx.send(f'sell {price} at {code}')

    @turnip.command()
    async def buy(self, ctx, price, code):
        await ctx.send(f'buy {price} at {code}')

    @turnip.command()
    async def stop(self, ctx):
        await ctx.send(f'stop')


def setup(bot):
    bot.add_cog(Turnips(bot))
