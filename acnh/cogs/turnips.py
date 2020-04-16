from datetime import datetime

import discord
from discord.ext import commands

from acnh.database.models import Turnip
from acnh.utils import create_embed

REPLACE_EMOJI = "♻️"


def set_footer(embed, ctx):
    embed.set_footer(text=f"{ctx.author} - <{ctx.author.id}>")


def parse_selling(is_selling):
    if is_selling:
        return "Selling"
    return "Buying"


class Turnips(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.group(invoke_without_command=False, pass_context=True)
    async def turnip(self, ctx):
        pass

    @turnip.group(invoke_without_command=False, pass_context=True)
    async def list(self, ctx):
        pass

    @turnip.command()
    async def info(self, ctx):
        pass

    @list.command()
    async def selling(self, ctx):
        pass

    @list.command()
    async def buying(self, ctx):
        pass

    @turnip.command()
    async def sell(self, ctx, price: int, code: str):
        await self.new_listing(ctx, price, code, True)

    @turnip.command()
    async def buy(self, ctx, price, code):
        await self.new_listing(ctx, price, code, False)

    @turnip.command()
    async def stop(self, ctx):
        await ctx.send(f"stop")

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
            value=f"{parse_selling(is_selling)} Turnips for {price} 🔔",
        )
        set_footer(embed, ctx)
        await ctx.send(embed=embed)

    async def add_replace_logic(self, ctx, listing, is_selling, price, code):
        embed = await create_embed(
            description=f"You already have an active listing. React with {REPLACE_EMOJI} to replace it."
        )
        embed.add_field(
            name="Old",
            value=f"{parse_selling(listing.is_selling)} for {listing.price} 🔔. Active since {datetime.now() - listing.open_time}",
            inline=False,
        )
        embed.add_field(
            name="New", value=f"{parse_selling(is_selling)} for {price} 🔔", inline=False
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
