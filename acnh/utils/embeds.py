import discord


async def create_embed(title=None, description=None, url=None) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, url=url)
    embed.colour = discord.Color(0x123456)
    return embed
