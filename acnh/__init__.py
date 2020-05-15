import asyncio
import random
from pathlib import Path

import acnh.database
import discord
from acnh.database.models import Guild
from acnh.utils import config, get_guild_prefix
from discord.ext import commands

__version__ = "0.3.2"

invite_link = "https://discordapp.com/api/oauth2/authorize?client_id={}&scope=bot&permissions=8192"

presence_strings = [
    "turnip stonks",
    "@Daisy help",
    "@Daisy turnip",
    "@Daisy villager marshal",
    "selling turnips",
]


async def get_prefix(_bot, message):
    prefix = config.prefix
    if not isinstance(message.channel, discord.DMChannel):
        prefix = get_guild_prefix(_bot, message.guild.id)
    return commands.when_mentioned_or(prefix)(_bot, message)


bot = commands.AutoShardedBot(command_prefix=get_prefix)


async def preload_guild_data():
    guilds = await Guild.query.gino.all()
    d = dict()
    for guild in guilds:
        d[guild.id] = {"prefix": guild.prefix}
    return d


@bot.event
async def on_ready():
    await database.setup()
    print(
        f"""Logged in as {bot.user}..
        Serving {len(bot.users)} users in {len(bot.guilds)} guilds
        Invite: {invite_link.format(bot.user.id)}
    """
    )
    bot.guild_data = await preload_guild_data()
    bot.loop.create_task(presence_task())


async def presence_task():
    while True:
        await bot.change_presence(
            activity=discord.Game(random.choice(presence_strings))
        )
        await asyncio.sleep(60)


def extensions():
    files = Path("acnh", "cogs").rglob("*.py")
    for file in files:
        yield file.as_posix()[:-3].replace("/", ".")


def load_extensions(_bot):
    for ext in extensions():
        try:
            _bot.load_extension(ext)
        except Exception as ex:
            print(f"Failed to load extension {ext} - exception: {ex}")


def run():
    load_extensions(bot)
    bot.run(config.token)
