import aiohttp
import discord
from discord.ext import commands

from acnh.utils import config

API_URL = "https://discordbots.org/api/bots/{bot_id}/stats"


class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = config.topgg_key
        if self.api_key is None:
            raise ValueError

    async def post_count(self):
        headers = {"Authorization": self.api_key}
        payload = {"server_count": len(self.bot.guilds)}
        async with aiohttp.ClientSession() as session:
            await session.post(
                API_URL.format(bot_id=self.bot.user.id), data=payload, headers=headers
            )

    @commands.Cog.listener()
    async def on_ready(self):
        await self.post_count()
        print(f"{type(self).__name__} Cog ready.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.post_count()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.post_count()


def setup(bot):
    bot.add_cog(TopGG(bot))
