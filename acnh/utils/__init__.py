from .config import Config
from .embeds import create_embed, wait_for_choice

config = Config()


def get_guild_prefix(_bot, guild_id):
    prefix = config.prefix
    guild_data = _bot.guild_data.get(guild_id, None)
    if guild_data is not None:
        prefix = guild_data.get("prefix", prefix)
    return prefix
