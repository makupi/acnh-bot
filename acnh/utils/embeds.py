import discord


async def create_embed(title=None, description=None, url=None) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, url=url)
    embed.colour = discord.Color(0xDE98E9)
    return embed


async def wait_for_choice(ctx, embed, choices):
    d = {}
    for index, match in enumerate(choices):
        d[f"{index}⃣"] = match[0]
    for k, v in d.items():
        embed.add_field(name=k, value=v, inline=True)

    msg = await ctx.send(embed=embed)
    for emoji in d.keys():
        await msg.add_reaction(emoji)

    def check(_reaction, _user):
        return (
            _reaction.message.id == msg.id
            and _user.id == ctx.author.id
            and _reaction.emoji in d.keys()
        )

    reaction, user = await ctx.bot.wait_for("reaction_add", check=check, timeout=300.0)
    try:
        await msg.clear_reactions()
    except discord.Forbidden:
        pass
    return d.get(reaction.emoji), msg
