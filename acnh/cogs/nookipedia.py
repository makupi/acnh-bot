import difflib

import aiohttp
import discord
from discord.ext import commands

from acnh.utils import config, create_embed, wait_for_choice
from fuzzywuzzy import process as fuzzy_search

# match to list of villagers with difflib.get_close_matches

VILLAGER_API = "https://nookipedia.com/api/villager/{name}/"
CATEGORY_API = (
    "https://nookipedia.com/w/api.php?action=query&list=categorymembers&&cmlimit=max&format=json&cmtitle"
    "=Category:{}"
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
    r = await fetch_json(CATEGORY_API.format("Villager"))
    member_list = r.get("query").get("categorymembers")
    villagers = []
    for member in member_list:
        name = member.get("title")
        if "Category" in name or "islander" in name:
            continue
        villagers.append(name)
    return villagers


async def query_critter_list() -> list:
    bugs = await fetch_json(CATEGORY_API.format("New_Horizons_fish"))
    fish = await fetch_json(CATEGORY_API.format("New_Horizons_bugs"))
    bug_list = bugs.get("query").get("categorymembers")
    fish_list = fish.get("query").get("categorymembers")
    critters = []
    for m in bug_list + fish_list:
        name = m.get("title")
        critters.append(name)
    return critters


class Nookipedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = config.nookipedia_key
        self.villagers = []
        self.critters = []

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")
        self.villagers = await query_villager_list()
        self.critters = await query_critter_list()
        print(self.critters)

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
        tmp = f"{name.capitalize()} (villager)"
        if tmp in self.villagers:
            return tmp, None
        return await search(ctx, name, self.villagers, "villager")

    async def find_critter(self, ctx, name):
        tmp = f"{name.capitalize()} (fish)"
        if tmp in self.critters:
            return tmp, None
        return await search(ctx, name, self.critters, "critter")


def setup(bot):
    bot.add_cog(Nookipedia(bot))
