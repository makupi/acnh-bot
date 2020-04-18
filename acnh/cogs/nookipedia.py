import aiohttp
import discord
from discord.ext import commands

from acnh.utils import config, create_embed

# match to list of villagers with difflib.get_close_matches

VILLAGER_API = "https://nookipedia.com/api/villager/{name}/?api_key={api_key}"


async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def fetch_villager(name, api_key):
    return await fetch_json(VILLAGER_API.format(name=name, api_key=api_key))


class Nookipedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = config.nookipedia_key

    async def query_villager_list(self) -> list:
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.command()
    async def villager(self, ctx, *, name: str):
        result = await fetch_villager(name, self.api_key)
        quote = result.get("quote", "")
        image = result.get("image", None)
        gender = result.get("gender", None)
        personality = result.get("personality", None)
        species = result.get("species", None)
        birthday = result.get("birthday", None)
        phrase = result.get("phrase", None)
        sign = result.get("sign", None)
        link = result.get("link", None)
        embed = await create_embed(title=name, description=quote, url=link)
        embed.set_thumbnail(url=image)
        embed.set_footer(text="Powered by https://nookipedia.com/")
        if gender:
            embed.add_field(name="Gender", value=gender)
        if species:
            embed.add_field(name="Species", value=species)
        if personality:
            embed.add_field(name="Personality", value=personality)
        if phrase:
            embed.add_field(name="Phrase", value=phrase)
        if birthday:
            embed.add_field(name="Birthday", value=f"{birthday} ({sign})")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Nookipedia(bot))
