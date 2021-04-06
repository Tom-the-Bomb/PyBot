import discord

import asyncio
import os
import typing
import json

from datetime import datetime as dt
from discord.ext import commands

import asyncio
import motor
from motor.motor_asyncio import AsyncIOMotorClient

def load_config():

    with open("config.json") as config:
        return json.load(config)

class PythonBot(commands.AutoShardedBot):

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        os.environ["JISHAKU_HIDE"] = "True"
        self.config = load_config()
        self.BotToken = self.config["TOKEN"]
        self._ClientSecret = self.config["SECRET"]
        self.launch_time = dt.utcnow() 
        self._timeformat = "%m/%d/%Y, %H:%M:%S"
        self.cluster = AsyncIOMotorClient(
            self.config["MONGO"]["CONNECTION_STRING"]
        )
        self.Tags = self.cluster["PyBot"]["Tag-system"]

    async def load_all_cogs(self):

        await self.wait_until_ready()
        try:
            self.load_extension("jishaku")
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    self.load_extension(f"cogs.{filename[:-3]}")
                    print(f" • cogs.{filename[:-3]} is loaded and ready")
            return 0
        except:
            return 1

    async def NumMembers(self):
        return sum((g.member_count for g in self.guilds))

    async def uptime(self):
        delta_uptime = dt.utcnow() - self.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        return days, hours, minutes, seconds
    
    async def change_status(self):
        await self.wait_until_ready()
        await self.change_presence(
            status=discord.Status.idle, 
            activity = discord.Game(
                f"Evaluating code for {await self.NumMembers()} users in {len(self.guilds)} servers"
            )
        )

    async def on_connect(self):

        LogTime = dt.now().strftime(self._timeformat)
        print(
            f"{self.user} is connected at {LogTime}"
        )
        
    async def on_ready(self):

        LogTime = dt.now().strftime(self._timeformat)
        print(
            f"{self.user} is online at {LogTime}"
        )
        LoadStatus = await self.load_all_cogs()
        print(f"Cogs loaded with exit status {LoadStatus}")
        await self.change_status()

    async def on_guild_join(self, guild):
        
        await self.Tags.insert_one({"_guild_id_": guild.id})
        await self.change_status()
        channel = self.get_channel(id=810977913025200148)
        await channel.send(f"Joined `{guild.name}`")
        channel = guild.system_channel or discord.utils.get(guild.channels, name="general") or guild.text_channels[0]
        try:
            return await channel.send(
                embed = discord.Embed(
                    title="Thanks for adding me to your server!", 
                    description=r'''
                    ```
My prefix is % but you can also mention me as prefix!
Do `%help` for help and %info for info!
To get started with tags  : %tag create
To get started with To-do : %todo add
                    ```
                    ''', 
                    url="https://dsc.gg/pybot"
                )
            )
        except:
            return

    async def on_guild_remove(self, guild):
        
        await self.Tags.delete_one({"_guild_id_": guild.id})
        await self.change_status()
        channel = self.get_channel(id=810977913025200148)
        await channel.send(f"left `{guild.name}`")


PyBot = PythonBot(
    command_prefix = commands.when_mentioned_or("%"),
    intents = discord.Intents.all(),
    help_command = None,
    case_insensitive = True,
    description = "A bot to help python developers",
)

if __name__ == "__main__":
    PyBot.run(PyBot.BotToken)