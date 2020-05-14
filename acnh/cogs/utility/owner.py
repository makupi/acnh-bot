import subprocess
import sys

import acnh.database as db
import discord
from acnh.utils import config, create_embed
from discord.ext import commands


def fix_cog_path(cog):
    if not cog.startswith("acnh.cogs."):
        if not cog.startswith("cogs."):
            return "acnh.cogs." + cog
        return "acnh." + cog
    return cog


class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.command()
    async def defaultprefix(self, ctx, new_prefix: str):
        old_prefix = config.prefix
        config.prefix = new_prefix
        config.store()
        embed = await create_embed(title="Changing default prefix")
        embed.add_field(name="From", value=old_prefix)
        embed.add_field(name="To", value=new_prefix)
        await ctx.send(embed=embed)

    @commands.command()
    async def shutdown(self, ctx):
        await db.shutdown()
        embed = await create_embed(title="Shutting down..")
        await ctx.send(embed=embed)

        sys.exit()

    @commands.command()
    async def load(self, ctx, cog: str):
        embed = await create_embed(title=f"Load Extension {cog}")
        try:
            self.bot.load_extension(fix_cog_path(cog))
        except (commands.ExtensionAlreadyLoaded, commands.ExtensionNotFound) as ex:
            embed.add_field(name="Error", value=f"{type(ex).__name__} - {ex}")
        else:
            embed.description = "Success"
        await ctx.send(embed=embed)

    @commands.command()
    async def unload(self, ctx, cog: str):
        embed = await create_embed(title=f"Unload Extension {cog}")
        try:
            self.bot.unload_extension(fix_cog_path(cog))
        except commands.ExtensionNotLoaded as ex:
            embed.add_field(name="Error", value=f"{type(ex).__name__} - {ex}")
        else:
            embed.description = "Success"
        await ctx.send(embed=embed)

    @commands.command()
    async def reload(self, ctx, cog: str):
        embed = await create_embed(title=f"Reload Extension {cog}")
        try:
            self.bot.reload_extension(fix_cog_path(cog))
        except (commands.ExtensionNotLoaded, commands.ExtensionNotFound) as ex:
            embed.add_field(name="Error", value=f"{type(ex).__name__} - {ex}")
        else:
            embed.description = "Success"
        await ctx.send(embed=embed)

    @commands.command()
    async def cogs(self, ctx):
        msg = ""
        for cog in self.bot.cogs:
            msg += f"- {cog}\n"
        embed = await create_embed(title="Loaded Extensions", description=msg)
        await ctx.send(embed=embed)

    @commands.command()
    async def exec(self, ctx, *command: str):
        embed = await create_embed(title=" ".join(command))
        try:
            with subprocess.Popen(
                [*list(command)], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as proc:
                out = proc.stdout.read().decode()[0:1994]  # max 2000 signs per message
                err = proc.stderr.read().decode()[0:1994]
                if out:
                    embed.add_field(name="stdout", value=out)
                if err:
                    embed.add_field(name="stderr", value=out)
        except Exception as ex:
            embed.add_field(name="Exception", value=str(ex))
        await ctx.send(embed=embed)

    @commands.command()
    async def setup(self, ctx):
        for guild in ctx.bot.guilds:
            _ = await db.query_guild(guild.id)


def setup(bot):
    bot.add_cog(Owner(bot))
