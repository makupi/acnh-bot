import discord
from discord.ext import commands

from acnh.utils import create_embed, get_guild_prefix


async def create_bot_help(embed, mapping):
    for cog, cmds in mapping.items():
        cmd_str = ""
        for cmd in cmds:
            if not cmd.hidden:
                cmd_str += f"`{cmd.name}`: {cmd.short_doc}\n"
        if cmd_str:
            embed.add_field(name=cog.qualified_name, value=cmd_str, inline=False)
    return embed


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    def get_bot_mapping(self):
        """Retrieves the bot mapping passed to :meth:`send_bot_help`."""
        bot = self.bot
        mapping = {cog: cog.get_commands() for cog in bot.cogs.values()}
        # mapping[None] = [c for c in bot.all_commands.values() if c.cog is None]
        return mapping

    @commands.command()
    async def help(self, ctx, command_name: str = None):
        """*Shows this help message*"""
        prefix = get_guild_prefix(ctx.bot, ctx.guild.id)
        embed = await create_embed(
            title="Help",
            description=f"*Use `{prefix}help <command-name>` to get a more detailed help for a specific command!*"
            f"\n`<value>` is for required arguments and `[value]` for optional arguments!",
        )
        embed.set_footer(
            text="Thank you for using Daisy <3", icon_url=self.bot.user.avatar_url
        )
        if command_name is not None:
            cmd = ctx.bot.all_commands.get(command_name)
            if cmd is not None:
                embed.add_field(name=cmd.name, value=cmd.help.format(prefix=prefix))
                return await ctx.send(embed=embed)
        embed = await create_bot_help(embed, self.get_bot_mapping())
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
