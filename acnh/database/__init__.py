from acnh.utils import config
from gino import Gino

db = Gino()

# import models so Gino registers them
import acnh.database.models  # isort:skip


async def setup():
    await db.set_bind(config.database)


async def shutdown():
    await db.pop_bind().close()


async def query_guild(guild_id: int):
    """: query guild, create if not exist"""
    guild = await models.Guild.get(guild_id)
    if guild is None:
        guild = await models.Guild.create(id=guild_id)
    return guild
