import discord
from discord.ext import commands

import os
import re
import traceback
import contextlib
from io import StringIO

class Developer(commands.Cog):

    def __init__(self, client):
        self.PyBot = client
        self.env = {}

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

    def update_env(self, ctx):

        self.env.update({
            "ctx": ctx, 
            "PyBot": self.PyBot, 
            "discord": discord, 
            "commands": commands, 
            "self": self, 
            "db": self.PyBot.cluster["PyBot"],
            "Tags": self.PyBot.cluster["PyBot"]["Tag-system"], 
            "Todo": self.PyBot.cluster["PyBot"]["To-do-system"], 
        })

    @commands.command(name="exec")
    @commands.is_owner()
    async def dev_eval(self, ctx, *, code: str):

        code = code.strip("`")

        if re.match('py(thon)?\n', code):
            code = "\n".join(code.split("\n")[1:])

        if not re.search(
            r"^(return|import|for|while|def|class|"
            r"from|exit|[a-zA-Z0-9]+\s*=)", 
            code, re.M
        ) and len(code.split("\n")) == 1:
            code = f"print({code})"

        self.update_env(ctx)
        
        with StringIO() as stream:
            try:
                with contextlib.redirect_stdout(stream):
                    exec(code, self.env)
                result = stream.getvalue()
            except Exception:
                result = traceback.format_exc()

            return await ctx.send(f"```py\n... \n{result}\n```")

def setup(client):
    client.add_cog(Developer(client))