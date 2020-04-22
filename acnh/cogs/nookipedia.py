import difflib
import json

import aiohttp
import discord
from discord.ext import commands

from acnh.utils import config, create_embed, wait_for_choice
from fuzzywuzzy import process as fuzzy_search

# match to list of villagers with difflib.get_close_matches

VILLAGER_API = "https://nookipedia.com/api/villager/{name}/"
CRITTER_API = "https://nookipedia.com/api/critter/{name}/"
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


async def fetch_critter(name, api_key):
    headers = {"X-API-KEY": api_key}
    return await fetch_json(CRITTER_API.format(name=name), headers=headers)


async def query_villager_list() -> list:
    r = await fetch_json(CATEGORY_API.format("Villagers"))
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


def split_string_categories(string):
    if ")" not in string:
        return string
    split = string.split(")")
    for s in split:
        if "New Horizons" in s:
            s = s.split("(")
            return s[0]
    return string.replace(")", ")\n")


async def search(ctx, name, lookup, category):
    if name.capitalize() in lookup:
        return name.capitalize(), None
    if name.title() in lookup:
        return name.title(), None
    matches = fuzzy_search.extract(name, lookup, limit=6)
    embed = await create_embed()
    if len(matches) == 1:
        return matches[0][0], None
    elif len(matches) == 0:
        embed.description = f"No matching {category} found!"
        await ctx.send(embed=embed)
        return None, None
    else:
        embed.description = f"Did you mean any of these {category}s?"
        embed.set_footer(text=f"React to choose one {category}!")
        return await wait_for_choice(ctx, embed, matches)


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
        embed = await create_embed(title=name, description=f"*{quote}*", url=link)
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

    @commands.command(aliases=["bug", "fish"])
    async def critter(self, ctx, *, name: str):
        """: Look up a critter by name
        Use ;critter Sea Bass to get information about the sea bass, bet it's at least a C+!"""
        await ctx.trigger_typing()
        name, msg = await self.find_critter(ctx, name)
        if name is None:
            return
        result = await fetch_critter(name, self.api_key)
        catch_phrase = result.get("caught")
        link = result.get("link")
        embed = await create_embed(
            title=name, description=f"*{catch_phrase}*", url=link
        )
        embed.set_thumbnail(url=result.get("image"))
        embed.set_footer(
            text="Powered by https://nookipedia.com/ (critter is currently in beta)"
        )
        time_year = result.get("time-year", None)
        time_day = result.get("time-day", None)
        rarity = result.get("rarity", None)
        price = result.get("price", None)
        shadow = result.get("shadow", None)
        location = result.get("location", None)
        #         embed.description = f"""```json
        # {json.dumps(result, indent=4)}
        # ```
        # """
        if time_year:
            value = split_string_categories(time_year)
            embed.add_field(name="Season", value=value, inline=False)
        if time_day:
            value = split_string_categories(time_day)
            embed.add_field(name="Daytime", value=value, inline=False)
        if rarity:
            value = split_string_categories(rarity)
            embed.add_field(name="Rarity", value=value, inline=False)
        if price:
            value = split_string_categories(price)
            embed.add_field(name="Sell Price", value=value, inline=False)
        if shadow:
            value = split_string_categories(shadow)
            embed.add_field(name="Shadow", value=value, inline=False)
        if location:
            value = split_string_categories(location)
            embed.add_field(name="Location", value=value, inline=False)

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
