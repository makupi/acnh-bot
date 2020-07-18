import discord
from discord.ext import commands

from acnh.database.models import Profile
from acnh.utils import create_embed, get_guild_prefix

FRUITS = {"apple": "🍎", "cherry": "🍒", "orange": "🍊", "pear": "🍐", "peach": "🍑"}


async def query_profile(user_id: int):
    """: query profile, create if not exist"""
    profile = await Profile.get(user_id)
    if profile is None:
        profile = await Profile.create(user_id=user_id)
    return profile


async def send_changed_embed(ctx, changed: str, before: str, after: str):
    embed = await create_embed(description=f"*{changed} changed*")
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.add_field(name="From", value=before)
    embed.add_field(name="To", value=after)
    await ctx.send(embed=embed)


def is_northern_str(is_northern):
    if is_northern is None:
        return None
    if is_northern:
        return "Northern"
    return "Southern"


def get_fruit(fruit: str):
    fruit_emoji = FRUITS.get(fruit)
    if fruit_emoji is None:
        return None
    return f"{fruit_emoji} {fruit.capitalize()}"


class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.group(invoke_without_command=True, pass_context=True)
    async def profile(self, ctx, user_check: discord.User = None):
        """*Look up your or your friends profile*

        `[user]` is optional and either a user-id or a user mention
        **Usage**: `{prefix}profile [user]`
        **Example**: `{prefix}profile`

        To setup your own profile use the following commands
        **Usage**: `{prefix}profile <island|name|fruit|hemisphere|fc> <value>`
        **Examples**:
            `{prefix}profile name Daisy`
            `{prefix}profile fruit cherry`
            `{prefix}profile hemisphere northern`
        """
        user = user_check
        if user is None:
            user = ctx.author
        profile = await query_profile(user.id)

        embed = await create_embed()
        if profile.island_name != "Not Set":
            embed.add_field(name="Island Name", value=profile.island_name)
        if profile.user_name != "Not Set":
            embed.add_field(name="Character Name", value=profile.user_name)
            embed.add_field(name="\u200c", value="\u200c")
        if is_northern_str(profile.is_northern):
            embed.add_field(name="Hemisphere", value=is_northern_str(profile.is_northern))
        if get_fruit(profile.fruit):
            embed.add_field(name="Fruit", value=get_fruit(profile.fruit))
            embed.add_field(name="\u200c", value="\u200c")
        if profile.flower:
            embed.add_field(name="Flower", value=profile.flower)
        if profile.airport:
            embed.add_field(name="Airport Color", value=profile.airport)
            embed.add_field(name="\u200c", value="\u200c")
        if profile.timezone:
            embed.add_field(name="Timezone", value=profile.timezone)
        if profile.friend_code != "Not Set":
            embed.add_field(name="Friend Code", value=profile.friend_code)

        if embed.fields:
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_footer(text=f"Profile of {user.name}#{user.discriminator}")
        else:
            if user_check:
                embed.description = f"{user_check.mention} hasn't configured their profile yet!"
            else:
                prefix = get_guild_prefix(self.bot, ctx.guild.id)
                embed.description = (
                    f"**You haven't configured your profile yet!**\n"
                    f"To configure your profile use: \n`{prefix}profile <island|name|fruit|hemisphere|fc> <value>`\n"
                    f"**Examples**:\n"
                    f"`{prefix}profile name Daisy`\n"
                    f"`{prefix}profile fruit cherry`\n"
                    f"`{prefix}profile hemisphere northern`\n"
                )
        await ctx.send(embed=embed)

    @profile.command()
    async def island(self, ctx, *, island_name: str):
        profile = await query_profile(ctx.author.id)
        await send_changed_embed(
            ctx, changed="Island name", before=profile.island_name, after=island_name,
        )
        await profile.update(island_name=island_name).apply()

    @profile.command(aliases=["name"])
    async def character(self, ctx, *, character_name: str):
        profile = await query_profile(ctx.author.id)
        await send_changed_embed(
            ctx, changed="Character name", before=profile.user_name, after=character_name,
        )
        await profile.update(user_name=character_name).apply()

    @profile.command()
    async def fruit(self, ctx, fruit: str):
        embed = await create_embed()
        if fruit not in FRUITS.keys():
            embed.description = f"Fruit `{fruit}` not found! Please use one of the following: \n"
            embed.description += f'`{", ".join(FRUITS.keys())}`'
            await ctx.send(embed=embed)
        else:
            profile = await query_profile(ctx.author.id)
            before = FRUITS.get(profile.fruit, "Not set")
            after = FRUITS.get(fruit)
            await profile.update(fruit=fruit).apply()
            await send_changed_embed(ctx, changed="Fruit", before=before, after=after)

    @profile.command(aliases=["location"])
    async def hemisphere(self, ctx, hemisphere: str):
        profile = await query_profile(ctx.author.id)
        before = profile.is_northern
        after = None
        if hemisphere.lower() in ["northern", "north"]:
            after = True
            await profile.update(is_northern=True).apply()
        elif hemisphere.lower() in ["southern", "south"]:
            after = False
            await profile.update(is_northern=False).apply()
        else:
            embed = await create_embed(description=f"Please use either `northern` or `southern`! ")
            if profile.is_northern is None:
                embed.description += "Currently not set!"
            else:
                embed.description += f"Currently set to {is_northern_str(profile.is_northern)}"
            await ctx.send(embed=embed)
        await send_changed_embed(
            ctx, changed="Hemisphere", before=is_northern_str(before), after=is_northern_str(after),
        )

    @profile.command(aliases=["fc", "code"])
    async def friendcode(self, ctx, friend_code: str):
        profile = await query_profile(ctx.author.id)
        friend_code = friend_code.upper()
        if "SW-" not in friend_code:
            friend_code = f"SW-{friend_code}"
        await send_changed_embed(
            ctx, changed="Friend code", before=profile.friend_code, after=friend_code,
        )
        await profile.update(friend_code=friend_code).apply()

    @profile.command()
    async def flower(self, ctx, *, flower: str):
        profile = await query_profile(ctx.author.id)
        before = profile.flower
        if not before:
            before = "Not Set"
        await profile.update(flower=flower).apply()
        await send_changed_embed(ctx, changed="Flower", before=before, after=profile.flower)

    @profile.command()
    async def airport(self, ctx, *, airport: str):
        profile = await query_profile(ctx.author.id)
        before = profile.airport
        if not before:
            before = "Not Set"
        await profile.update(airport=airport).apply()
        await send_changed_embed(ctx, changed="Airport Color", before=before, after=profile.airport)

    @profile.command()
    async def timezone(self, ctx, *, timezone: str):
        profile = await query_profile(ctx.author.id)
        before = profile.timezone
        if not before:
            before = "Not Set"
        await profile.update(timezone=timezone).apply()
        await send_changed_embed(ctx, changed="Timezone", before=before, after=profile.timezone)


def setup(bot):
    bot.add_cog(Profiles(bot))
