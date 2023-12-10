import discord
from discord.ext import commands, menus

import asyncio
import motor
from motor.motor_asyncio import AsyncIOMotorClient

class TagsPaginator(menus.ListPageSource):

    def __init__(self, ctx, entries, *, per_page=8):
        self.ctx = ctx
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = discord.Embed(
            title=f"- Tags in {self.ctx.guild.name} -",
            description = " • " + "\n • ".join(page[2:])
        )
        embed.set_footer(text=f"Page {menu.current_page+1}/{self.get_max_pages()}")
        return embed

class TagSystem(commands.Cog):

    def __init__(self, client):

        self.PyBot = client
        self.cluster = AsyncIOMotorClient(
            self.PyBot.config["MONGO"]["CONNECTION_STRING"]
        )
        self.Tags = self.cluster["PyBot"]["Tag-system"]

    @commands.group(
        name = "tag",
        description = "Tag-system for tagging info",
        invoke_without_command=True
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tag(self, ctx, *, tag: str):
        raw = tag
        guild = await self.Tags.find_one(
            {"_guild_id_": ctx.guild.id}
        )
        tag = guild.get(tag)
        if not tag:
            return await ctx.send(
                f"Could not find a tag named: `{raw}`"
            )
        else:
            return await ctx.send(
                content = tag[1],
                allowed_mentions = discord.AllowedMentions.none()
            )

    @tag.command(
        name = "create",
        description = "Creates a tag",
        aliases = ["add"],
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def create(self, ctx, *, name: str):

        guild = await self.Tags.find_one(
            {"_guild_id_": ctx.guild.id}
        )

        if len(name) > 100:
            return await ctx.send("Please keep the name length under 100 characters.")

        if guild.get(name):
            return await ctx.send("Oops looks like that tag already exists!")

        await ctx.send("What do you want the content of the tag to be? `Type it in the chat`")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            content = await self.PyBot.wait_for("message", timeout=300.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.reply("Looks like you took too long to respond!")

        try:
            await self.Tags.update_one(
                {"_guild_id_": ctx.guild.id},
                {
                    "$set": {
                        name: (ctx.author.id, content.content)
                    }
                }
            )
            return await ctx.send(f"Tag `{name}` created successfully.")
        except Exception as e:
            return await ctx.send(
                f"Oops looks like an error occured registering the tag:\n`{e}`\nPlease try again later."
            )

    @tag.command(
        name="edit",
        description="Edits an existing tag",
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def edit(self, ctx, *, tag: str):

        guild = await self.Tags.find_one(
            {"_guild_id_": ctx.guild.id}
        )

        raw = guild.get(tag)
        if not raw:
            return await ctx.send("Oops looks like that tag does not exist!")

        if raw[0] != ctx.author.id and not ctx.author.guild_permissions.manage_guild:
            return await ctx.send("You must have `manage server` to be able to edit other people's tags!")

        await ctx.send("What do you want the new content of the tag to be? `Type it in the chat`")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            content = await self.PyBot.wait_for("message", timeout=300.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.reply("Looks like you took too long to respond!")

        try:
            await self.Tags.update_one(
                {"_guild_id_": ctx.guild.id},
                {
                    "$set": {
                        tag: (raw[0], content.content)
                    }
                }
            )
            return await ctx.send(f"Tag `{tag}` edited successfully.")
        except Exception as e:
            return await ctx.send(
                f"Oops looks like an error occured registering the tag:\n`{e}`\nPlease try again later."
            )

    @tag.command(
        name="delete",
        description="deletes an existing tag",
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def delete(self, ctx, *, tag: str):

        guild = await self.Tags.find_one(
            {"_guild_id_": ctx.guild.id}
        )

        raw = guild.get(tag)
        if not raw:
            return await ctx.send("Oops looks like that tag does not exist!")

        if raw[0] != ctx.author.id and not ctx.author.guild_permissions.manage_guild:
            return await ctx.send("You must have `manage server` to be able to edit other people's tags!")

        try:
            await self.Tags.update_one(
                {"_guild_id_": ctx.guild.id},
                {"$unset": {tag: ""}}
            )
            return await ctx.send(f"Tag `{tag}` deleted successfully.")
        except Exception as e:
            return await ctx.send(
                f"Oops looks like an error occured registering the tag:\n`{e}`\nPlease try again later."
            )

    @tag.command(
        name="info",
        description="retrives some info on a tag"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx, *, tag: str):
        guild = await self.Tags.find_one(
            {"_guild_id_": ctx.guild.id}
        )

        raw = guild.get(tag)
        if not raw:
            return await ctx.send("Oops looks like that tag does not exist!")

        owner = ctx.guild.get_member(raw[0])

        embed = discord.Embed(
            title=f"Tag | {tag}",
            description=f"```ini\n[ Owner ] : {owner}\n[ Name ]  : {tag}\n[ Usage ] : %tag {tag}\n```"
        )
        return await ctx.send(embed=embed)

    @commands.command(
        name="tags",
        description="fetches all the tags in the server",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tags(self, ctx):
        guild = await self.Tags.find_one(
            {"_guild_id_": ctx.guild.id}
        )
        tags = [tag for tag in guild]

        if len(tags) <= 2:
            return await ctx.send("This server does not have any tags yet! Create one by doing `%tag create`")

        pages = TagsPaginator(ctx=ctx, entries=tags)
        paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)
        return await paginator.start(ctx)

def setup(client):
    client.add_cog(TagSystem(client))