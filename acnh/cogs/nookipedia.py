from discord.ext import commands

from acnh.utils import config, create_embed, wait_for_choice
from fuzzywuzzy import process as fuzzy_search
from nookipedia import Nookipedia as NookipediaAPI


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
        self.api = NookipediaAPI(api_key=config.nookipedia_key, cached_api=True)
        self.villagers = list()
        self.critters = list()
        self.personality_data = dict()

    @commands.Cog.listener()
    async def on_ready(self):
        self.villagers = await self.query_villager_list()
        self.critters = await self.query_critter_list()
        self.personality_data = await self.query_personalities()
        print(f"{type(self).__name__} Cog ready.")

    @commands.command("testall", hidden=True)
    @commands.is_owner()
    async def test_all(self, ctx):
        villager_command = self.bot.get_command("villager")
        critter_command = self.bot.get_command("critter")
        for name in self.villagers:
            await ctx.send(f"testing command with {name}")
            await villager_command.callback(self, ctx, name=name)
        # for name in self.critters:
        #     await critter_command.callback(self, ctx, name=name)

    @commands.command()
    async def villager(self, ctx, *, name: str):
        """*Look up a villager by name*

        **Usage**: `{prefix}villager <name>`
        **Example**: `{prefix}villager marshal` """
        await ctx.trigger_typing()
        name, msg = await self.find_villager(ctx, name)
        if name is None:
            return
        v = await self.api.get_villager(name)
        embed = await create_embed(title=name, url=v.link)
        if v.quote:
            embed.description = f"*{v.quote}*"
        embed.set_thumbnail(url=v.image)
        embed.set_footer(text="Powered by https://nookipedia.com/")
        if v.gender:
            embed.add_field(name="Gender", value=v.gender)
        if v.species:
            embed.add_field(name="Species", value=v.species)
        if v.personality:
            embed.add_field(name="Personality", value=v.personality)
        if v.phrase:
            embed.add_field(name="Phrase", value=v.phrase)
        if v.birthday:
            embed.add_field(name="Birthday", value=f"{v.birthday} ({v.sign})")
        if msg is None:
            await ctx.send(embed=embed)
        else:
            await msg.edit(embed=embed)

    @commands.command(aliases=["bug", "fish"])
    async def critter(self, ctx, *, name: str):
        """*Look up a critter by name*

        **Usage**: `{prefix}critter <name>`
        **Example**: `{prefix}critter sea bass` """
        await ctx.trigger_typing()
        name, msg = await self.find_critter(ctx, name)
        if name is None:
            return
        c = await self.api.get_critter(name)
        embed = await create_embed(title=name, url=c.link)
        if c.caught:
            embed.description = f"*{c.caught}*"
        embed.set_thumbnail(url=c.image)
        embed.set_footer(
            text="Powered by https://nookipedia.com/ (critter is currently in beta)"
        )
        if c.time_year:
            value = split_string_categories(c.time_year)
            embed.add_field(name="Season", value=value, inline=False)
        if c.time_day:
            value = split_string_categories(c.time_day)
            embed.add_field(name="Daytime", value=value, inline=False)
        if c.rarity:
            value = split_string_categories(c.rarity)
            embed.add_field(name="Rarity", value=value, inline=False)
        if c.price:
            value = split_string_categories(c.price)
            embed.add_field(name="Sell Price", value=value, inline=False)
        if c.shadow:
            value = split_string_categories(c.shadow)
            embed.add_field(name="Shadow", value=value, inline=False)
        if c.location:
            value = split_string_categories(c.location)
            embed.add_field(name="Location", value=value, inline=False)

        if msg is None:
            await ctx.send(embed=embed)
        else:
            await msg.edit(embed=embed)

    @commands.command()
    async def personalities(self, ctx):
        """*Get a list of personalities*

        **Example**: `{prefix}personalities` """
        embed = await create_embed(title="Personalities")
        desc = ""
        for k in self.personality_data.keys():
            desc += f" - {k}\n"
        embed.description = desc
        await ctx.send(embed=embed)

    @commands.command()
    async def personality(self, ctx, name: str):
        """*Get all villagers with a certain personality*

        **Usage**: `{prefix}personality <name>`
        **Example**: `{prefix}personality jock` """
        name = name.capitalize()
        embed = await create_embed()
        if name not in self.personality_data:
            embed.description = f"Personality `{name}` not found."
            await ctx.send(embed=embed)
            return
        embed.title = f"{name} villagers"
        data = self.personality_data.get(name)
        counter = 0
        msg = "```"
        for name in data:
            msg += f"{name:^10}\t"
            counter += 1
            if counter == 4:
                msg += "\n"
                counter = 0
        msg += "```"

        embed.description = msg
        embed.set_footer(text="Powered by https://nookipedia.com/")
        await ctx.send(embed=embed)

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

    async def query_villager_list(self) -> list:
        villagers = await self.api.get_category("Villagers")
        for villager in villagers:
            if "Category" in villager or "islander" in villager.lower():
                villagers.remove(villager)
        return villagers

    async def query_critter_list(self) -> list:
        bugs = await self.api.get_category("New_Horizons_fish")
        fish = await self.api.get_category("New_Horizons_bugs")
        return bugs + fish

    async def query_personalities(self) -> dict:
        pers = await self.api.get_category("Personalities")
        personalities = dict()
        for per in pers:
            personalities[per] = await self.api.get_category(f"{per}_villagers")
        return personalities


def setup(bot):
    bot.add_cog(Nookipedia(bot))
