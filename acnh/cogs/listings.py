from datetime import datetime

import discord
from discord.ext import commands

import acnh.database as db
from acnh.database.models import Guild, Listing
from acnh.utils import create_embed, get_guild_prefix


def parse_timedelta(td):
    minutes = round(td.seconds / 60)
    tmp = f"{minutes} minute"
    if minutes > 1:
        tmp += "s"
    return tmp


async def query_listings(guild_id: int):
    guild = await db.query_guild(guild_id)
    if guild.local_turnips:
        query = Listing.query.where(Listing.guild_id == guild_id)
    else:
        query = Listing.load(guild=Guild).query.where(Guild.local_turnips == False)
    return await query.gino.all()


def set_footer(embed, ctx):
    embed.set_footer(text=f"{ctx.author} - <{ctx.author.id}>")


class Listings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    async def check_user_banned(self, ctx):
        if ctx.author.id in self.bot.turnip_banned_users:
            embed = await create_embed(
                description="Sorry, you are currently banned due to repeated offenses. Please message maku#0001 for "
                "an appeal. "
            )
            await ctx.send(embed=embed)
            return True
        return False

    @commands.command()
    async def open(self, ctx, dodo_code: str, *, message: str):
        """*Open a custom listing*

        **Usage**: `{prefix}open <dodo-code> <message>`
        **Example**: `{prefix}open 123456 Hey come check out my Island!`"""
        if await self.check_user_banned(ctx):
            return
        prefix = get_guild_prefix(self.bot, ctx.guild.id)
        listing = await Listing.get(ctx.author.id)
        if listing:
            pass
        await Listing.create(
            user_id=ctx.author.id,
            guild_id=ctx.guild.id,
            invite_key=dodo_code,
            message=message,
            open_time=datetime.now(),
        )
        embed = await create_embed(
            description=f"Listing created. Please use `{prefix}close` once you're done!"
        )
        set_footer(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command()
    async def close(self, ctx):
        """*Close your previously opened listing*

        **Usage**: `{prefix}close"""
        listing = await Listing.get(ctx.author.id)
        if listing:
            await listing.delete()
        embed = await create_embed(description="Listing closed. Thank you for using Daisy <3")
        set_footer(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command()
    async def listings(self, ctx):
        """*List currently open custom listings*

        **Usage**: `{prefix}listings`"""
        listings = await query_listings(ctx.guild.id)
        embed = await create_embed(title="*Active listings*")
        if len(listings) == 0:
            embed.description = "*Currently no active listings!*"
        for listing in listings[:10]:
            user = self.bot.get_user(listing.user_id)
            user_str = f"**User**: {user.name}#{user.discriminator} <{user.id}>"
            if user is None:
                user_str = f"**User**: <{listing.user_id}>"
            embed.add_field(
                name=f"Dodo Code: **{listing.invite_key}**",
                value=f"**Message**: *{listing.message}*\n{user_str}\n"
                f"**Open since**: {parse_timedelta(datetime.now() - listing.open_time)}",
                inline=False,
            )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Listings(bot))
