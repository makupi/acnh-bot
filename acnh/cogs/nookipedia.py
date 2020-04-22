import difflib

import aiohttp
import discord
from discord.ext import commands

from acnh.utils import config, create_embed, wait_for_choice
from fuzzywuzzy import process as fuzzy_search

# match to list of villagers with difflib.get_close_matches

VILLAGER_API = "https://nookipedia.com/api/villager/{name}/"
VILLAGER_CATEGORY_LIST = (
    "https://nookipedia.com/w/api.php?action=query&list=categorymembers&&cmlimit=max&cmtitle"
    "=Category:Villagers&format=json"
)


async def fetch_json(url, headers=None):
    if headers is None:
        headers = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()


async def fetch_villager(name, api_key):
    header = {"X-API-KEY": api_key}
    return await fetch_json(VILLAGER_API.format(name=name), headers=header)


async def query_villager_list() -> list:
    r = await fetch_json(VILLAGER_CATEGORY_LIST)
    member_list = r.get("query").get("categorymembers")
    villagers = []
    for member in member_list:
        name = member.get("title")
        if "Category" in name or "islander" in name:
            continue
        villagers.append(name)
    return villagers


class Nookipedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = config.nookipedia_key
        self.villagers = []

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")
        self.villagers = await query_villager_list()

    @commands.command()
    async def villager(self, ctx, *, name: str):
        """: Look up a villager by name
        Use ;villager marshal to get information about marshal!"""
        await ctx.trigger_typing()
        name, msg = await self.find_villager(ctx, name)
        if name is None:
            return
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
        if msg is None:
            await ctx.send(embed=embed)
        else:
            await msg.edit(embed=embed)

    async def find_villager(self, ctx, name):
        # check exact match
        if name.capitalize() in self.villagers:
            return name.capitalize(), None
        tmp = f"{name.capitalize()} (villager)"
        if tmp in self.villagers:
            return tmp, None
        # matches = difflib.get_close_matches(name, self.villagers, n=6)
        matches = fuzzy_search.extract(name, self.villagers, limit=6)
        embed = await create_embed()
        if len(matches) == 1:
            return matches[0][0], None
        elif len(matches) == 0:
            embed.description = "No matching villager found!"
            await ctx.send(embed=embed)
            return None, None
        else:
            embed.description = "Did you mean any of these villagers?"
            embed.set_footer(text="React to choose one villager!")
            return await wait_for_choice(ctx, embed, matches)


def setup(bot):
    bot.add_cog(Nookipedia(bot))
