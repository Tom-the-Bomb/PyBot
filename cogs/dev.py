import traceback

import discord
from io import BytesIO
from discord.ext import commands
import os

from jishaku import codeblocks
from fstop.tests.test import Runner

class Developer(commands.Cog):

    def __init__(self, client):
        self.PyBot = client
        self.runner = Runner()

    @commands.command(name="load")
    @commands.is_owner()
    async def load(self, ctx, extension: str):
        
        try:
            self.PyBot.load_extension("cogs." + extension)
            await ctx.send(f'`➡️ cogs.{extension}` loaded successfully')
        except Exception as e:
            await ctx.send(f'An error has occured: {e}')

    @commands.command(name="unload")
    @commands.is_owner()
    async def unload(self, ctx, extension: str):
        
        try:
            self.PyBot.unload_extension("cogs." + extension)
            await ctx.send(f'`➡️ cogs.{extension}` unloaded successfully')
        except Exception as e:
            await ctx.send(f'An error has occured: {e}')

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, extension: str):
        
        try:
            if extension.lower() == 'all':
                for filename in os.listdir("./cogs"):
                    if filename.endswith(".py"):
                        await self.PyBot.reload_extension(f"cogs.{filename[:-3]}")
            else:
                self.PyBot.reload_extension("cogs." + extension)
                await ctx.send(f"`🔁 cogs.{extension}` successfully reloaded")
        except Exception as e:
            await ctx.send(f'An error has occured: {e}')

    @commands.command(name="fs")
    @commands.check(lambda ctx: ctx.author.id in (693987130036453398, 414556245178056706) or ctx.bot.is_owner(ctx.author))
    async def fs(self, ctx, *, code: codeblocks.codeblock_converter):
        try:
            _ = self.runner.execute(
                code.content, 
                streams = [
                    BytesIO(await ctx.author.avatar_url_as(format="png").read()),
                ]
            )
        except Exception as exc:
            exc = traceback.format_exception(exc.__class__, exc, exc.__traceback__)
            exc = '\n'.join(exc)
            await ctx.send(f"```py\n{exc}\n```")
        else:
            try:
                await ctx.send(file=discord.File(self.runner.streams[0], "0.gif"))
            except IndexError:
                await ctx.send(_)
        finally:
            self.runner.reset()

def setup(client):
    client.add_cog(Developer(client))