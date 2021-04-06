
from discord.ext import commands
import os

class Developer(commands.Cog):

    def __init__(self, client):
        self.PyBot = client

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

def setup(client):
    client.add_cog(Developer(client))