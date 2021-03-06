import sys
import time
from datetime import datetime

import discord
from discord.ext import commands

import acnh.database as db
from acnh.utils import create_embed, get_guild_prefix

PY_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now().replace(microsecond=0)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.command()
    async def ping(self, ctx):
        """*Current ping and latency of the bot*

        **Example**: `{prefix}ping`"""
        embed = await create_embed()
        before_time = time.time()
        msg = await ctx.send(embed=embed)
        latency = round(self.bot.latency * 1000)
        elapsed_ms = round((time.time() - before_time) * 1000) - latency
        embed.add_field(name="ping", value=f"{elapsed_ms}ms")
        embed.add_field(name="latency", value=f"{latency}ms")
        await msg.edit(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        """*Current uptime of the bot*

        **Example**: `{prefix}uptime`"""
        current_time = datetime.now().replace(microsecond=0)
        embed = await create_embed(
            description=f"Time since I went online: {current_time - self.start_time}."
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def starttime(self, ctx):
        """*When the bot was started*

        **Example**: `{prefix}starttime`"""
        embed = await create_embed(description=f"I'm up since {self.start_time}.")
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx):
        """*Shows stats and infos about the bot*

        **Example**: `{prefix}info`"""
        embed = await create_embed(title="Daisy")
        guild = await db.query_guild(ctx.guild.id)
        turnip_config = "global"
        if guild.local_turnips:
            turnip_config = "local"
        embed.url = f"https://top.gg/bot/{self.bot.user.id}"
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(
            name="Bot Stats",
            value=f"```py\n"
            f"Guilds: {len(self.bot.guilds)}\n"
            f"Users: {len(self.bot.users)}\n"
            f"Shards: {self.bot.shard_count}\n"
            f"Shard ID: {ctx.guild.shard_id}```",
            inline=False,
        )
        embed.add_field(
            name=f"Server Configuration",
            value=f"```\n"
            f"Prefix: {get_guild_prefix(self.bot, ctx.guild.id)}\n"
            f"Turnip Trading: {turnip_config}```",
            inline=False,
        )
        embed.add_field(
            name="Activity",
            value=f"```py\n"
            f"Processing {self.bot.active_commands} commands\n"
            f"{self.bot.total_commands} commands since startup```",
            inline=False,
        )
        embed.add_field(
            name="Software Versions",
            value=f"```py\n"
            f"Daisy: {self.bot.version}\n"
            f"discord.py: {discord.__version__}\n"
            f"Python: {PY_VERSION}```",
            inline=False,
        )
        embed.add_field(
            name="Links",
            value=f"[Invite]({self.bot.invite}) | "
            f"[Vote](https://top.gg/bot/{self.bot.user.id}/vote) | "
            f"[Support](https://discord.gg/vU7pDXB) | "
            f"[Ko-fi](https://ko-fi.com/makubob) | "
            f"[Github](https://github.com/makupi) | "
            f"[Twitter](https://twitter.com/makubob)",
            inline=False,
        )
        embed.set_footer(text="Thank you for using Daisy <3", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["socials", "links", "support"])
    async def invite(self, ctx):
        """*Shows invite link and other socials for the bot*

        **Aliases**: `socials`, `links`, `support`
        **Example**: `{prefix}invite`"""
        embed = await create_embed()
        embed.description = (
            f"[Invite]({self.bot.invite}) | "
            f"[Vote](https://top.gg/bot/431485759304892416/vote) | "
            f"[Support](https://discord.gg/vU7pDXB) | "
            f"[Ko-fi](https://ko-fi.com/makubob) | "
            f"[Github](https://github.com/makupi) | "
            f"[Twitter](https://twitter.com/makubob)"
        )
        embed.set_footer(text="Thank you for using Daisy <3", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
