from gino import Gino
from acnh.utils import config

db = Gino()

# import models so Gino registers them
import acnh.database.models  # isort:skip


async def setup():
    await db.set_bind(config.database)


async def shutdown():
    await db.pop_bind().close()
