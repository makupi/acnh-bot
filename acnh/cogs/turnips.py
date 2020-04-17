from datetime import datetime

import discord
from discord.ext import commands

from acnh.database.models import Turnip
from acnh.utils import create_embed, get_guild_prefix

REPLACE_EMOJI = "♻️"
BELL_EMOJI = "🔔"


def set_footer(embed, ctx):
    embed.set_footer(text=f"{ctx.author} - <{ctx.author.id}>")


def parse_selling(is_selling):
    if is_selling:
        return "Selling"
    return "Buying"


def add_listings(embed, listings):
    if len(listings) == 0:
        embed.description = (
            "*Currently no active listings for this category. Please try again later!*"
        )
    for listing in listings:
        embed.add_field(
            name=f"{listing.price} {BELL_EMOJI}",
            value=f"Invite Code: {listing.invite_key} - Active since: {datetime.now() - listing.open_time}",
            inline=False,
        )


class Turnips(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.group(invoke_without_command=True, pass_context=True)
    async def turnip(self, ctx):
        await self.info(ctx)

    @turnip.group(invoke_without_command=True, pass_context=True)
    async def list(self, ctx):
        await self.selling(ctx)
        await self.buying(ctx)

    @list.command()
    async def selling(self, ctx):
        listings = (
            await Turnip.query.where(Turnip.is_selling)
            .order_by(Turnip.price.desc())
            .gino.all()
        )
        embed = await create_embed(title="*Listings for Buying*")
        add_listings(embed, listings)
        await ctx.send(embed=embed)

    @list.command()
    async def buying(self, ctx):
        listings = (
            await Turnip.query.where(Turnip.is_selling is False)
            .order_by(Turnip.price.asc())
            .gino.all()
        )
        embed = await create_embed(title="*Listings for Selling*")
        add_listings(embed, listings)
        await ctx.send(embed=embed)

    @turnip.command()
    async def info(self, ctx):
        prefix = get_guild_prefix(self.bot, ctx.guild.id)
        embed = await create_embed(
            description=f"""Use the commands below to start trading Turnips! Don't forget to stop your listing once you're done. 
**Commands**
```
- {prefix}turnip sell/buy <price> <invite-code>
    - {prefix}turnip sell 600 6c63f04f
    - {prefix}turnip buy 90 6c63f04f
- {prefix}turnip list
    Lists both selling and buying listings
- {prefix}turnip list selling/buying
    Lists either selling or buying
- {prefix}turnip stop
    Stop your active listing. Please use this once your done!
```
**Active listings**
"""
        )
        selling_count = await Turnip.query.where(Turnip.is_selling).gino.all()
        buying_count = await Turnip.query.where(Turnip.is_selling is False).gino.all()
        embed.add_field(name="Selling", value=str(len(selling_count)))
        embed.add_field(name="Buying", value=str(len(buying_count)))
        await ctx.send(embed=embed)

    @turnip.command()
    async def sell(self, ctx, price: int, code: str):
        await self.new_listing(ctx, price, code, True)

    @turnip.command()
    async def buy(self, ctx, price, code):
        await self.new_listing(ctx, price, code, False)

    @turnip.command()
    async def stop(self, ctx):
        listing = await Turnip.get(ctx.author.id)
        if listing is not None:
            await listing.delete()
        embed = await create_embed(
            description="Listing deleted. Thank you for participating. <3"
        )
        set_footer(embed, ctx)
        await ctx.send(embed=embed)

    async def new_listing(self, ctx, price, code, is_selling):
        listing = await Turnip.get(ctx.author.id)
        if listing is not None:
            await self.add_replace_logic(ctx, listing, True, price, code)
            await listing.delete()
        await Turnip.create(
            user_id=ctx.author.id,
            guild_id=ctx.guild.id,
            is_selling=is_selling,
            invite_key=code,
            price=price,
            open_time=datetime.now(),
        )
        embed = await create_embed(
            description="*Please use the `turnip stop` command once you're done.*"
        )
        embed.add_field(
            name="New Listing",
            value=f"{parse_selling(is_selling)} Turnips for {price} {BELL_EMOJI}",
        )
        set_footer(embed, ctx)
        await ctx.send(embed=embed)

    async def add_replace_logic(self, ctx, listing, is_selling, price, code):
        embed = await create_embed(
            description=f"You already have an active listing. React with {REPLACE_EMOJI} to replace it."
        )
        embed.add_field(
            name="Old",
            value=f"{parse_selling(listing.is_selling)} for {listing.price} {BELL_EMOJI}. Active since {datetime.now() - listing.open_time}",
            inline=False,
        )
        embed.add_field(
            name="New",
            value=f"{parse_selling(is_selling)} for {price} {BELL_EMOJI}",
            inline=False,
        )
        set_footer(embed, ctx)
        msg = await ctx.send(f"{ctx.author.mention}", embed=embed)

        def check(reaction, user):
            return (
                reaction.message.id == msg.id
                and user.id == ctx.author.id
                and str(reaction.emoji) == REPLACE_EMOJI
            )

        await msg.add_reaction(REPLACE_EMOJI)
        await self.bot.wait_for("reaction_add", check=check, timeout=60.0)
        await msg.delete()


def setup(bot):
    bot.add_cog(Turnips(bot))