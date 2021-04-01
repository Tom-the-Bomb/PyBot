import discord
from discord.ext import commands, menus

from datetime import datetime as dt
import asyncio
import motor
from motor.motor_asyncio import AsyncIOMotorClient

class TodoPaginator(menus.ListPageSource):

    def __init__(self, ctx, entries, *, per_page=8):
        self.ctx = ctx
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = discord.Embed(
            title=f"`{self.ctx.author.name}'s` To-do list", 
            description = "\n".join(page), 
            timestamp = dt.utcnow()
        )
        embed.set_footer(text=f"Page {menu.current_page+1}/{self.get_max_pages()}")
        return embed

class ToDoSystem(commands.Cog):

    def __init__(self, client):

        self.PyBot = client
        self.cluster = AsyncIOMotorClient(
            self.PyBot.config["MONGO"]["CONNECTION_STRING"]
        )
        self.Todo = self.cluster["PyBot"]["To-do-system"]

    @commands.group(
        name="todo",
        invoke_without_command=True, 
        description="Shows your current todo list"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def todo(self, ctx):
        user = await self.Todo.find_one(
            {"user": ctx.author.id}
        )

        if not user:
            await self.Todo.insert_one(
                {
                    "user": ctx.author.id, "todo": []
                }
            )
            return await ctx.send(
                "You do not have a todo list yet!\nStart by doing `%todo add`"
            )

        else:
            todo = [
                f"**[{i}.]({item[0]})** {item[1]}" for i, item in enumerate(user["todo"], 1)
            ]

            pages = TodoPaginator(ctx=ctx, entries=todo)
            paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)
            return await paginator.start(ctx)

    @todo.command(
        name="add",
        description="adds a todo item"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def add(self, ctx, *, content: str):
        user = await self.Todo.find_one(
            {"user": ctx.author.id}
        )

        if not user:
            await self.Todo.insert_one(
                {
                    "user": ctx.author.id, "todo": []
                }
            )
        if len(content) > 220:
            return await ctx.send("Please keep the to-do content under 220 characters!")
        try:
            await self.Todo.update_one(
                {"user": ctx.author.id}, 
                {"$push": {"todo": (ctx.message.jump_url, content) }}
            )
            return await ctx.send(
                f"Successfully updated your **To-do list:**\n`{content}`"
            )
        except Exception as e:
            return await ctx.send(
                f"Oops looks like an error occured registering the todo-item:\n`{e}`\nPlease try again later."
            )

    @todo.command(
        name="delete",
        aliases=["remove"],
        description="Deletes a todo item"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def delete(self, ctx, index: str):

        user = await self.Todo.find_one(
            {"user": ctx.author.id}
        )

        if not user:
            await self.Todo.insert_one(
                {
                    "user": ctx.author.id, "todo": []
                }
            )
            return await ctx.send(
                "You do not have a todo list yet!\nStart by doing `%todo add`"
            )
        else:
            if index.lower() == "all":
                try:
                    await self.Todo.update_one(
                        {"user": ctx.author.id}, 
                        {"$set": {"todo": []}}
                    )
                    return await ctx.send(
                        f"Successfully cleared your to-do list"
                    )
                except Exception as e:
                    return await ctx.send(
                        f"Oops looks like an error occured clearing the list:\n`{e}`\nPlease try again later."
                    )
            else:
                if not index.isdigit():
                    return await ctx.send("Indexes must be numbers!\nHowever you can do `%todo delete all` to clear your list")
                index = int(index)
                if index < 1:
                    return await ctx.send("Indexes must be `1` or greater...")
                index -= 1

                try:
                    item = user["todo"][index]
                except IndexError:
                    return await ctx.send("Looks like that index doesn't exist on your list!")
                try:
                    await self.Todo.update_one(
                        {"user": ctx.author.id}, 
                        {"$pull": {"todo": item}}
                    )
                    return await ctx.send(
                        f"Successfully deleted to-do index: `{index+1}`"
                    )
                except Exception as e:
                    return await ctx.send(
                        f"Oops looks like an error occured registering the todo-item:\n`{e}`\nPlease try again later."
                    )

    @todo.command(
        name="edit",
        description="edits a todo item"
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def edit(self, ctx, index: int, *, content: str):
        user = await self.Todo.find_one(
            {"user": ctx.author.id}
        )
        if not user:
            await self.Todo.insert_one(
                {
                    "user": ctx.author.id, "todo": []
                }
            )
            return await ctx.send(
                "You do not have a todo list yet!\nStart by doing `%todo add`"
            )
        if len(content) > 220:
            return await ctx.send("Please keep the to-do content under 220 characters!")
        else:
            try:
                if index < 1:
                    return await ctx.send("Indexes must be `1` or greater...")
                index -= 1
                items = user["todo"]
                items[index] = (ctx.message.jump_url, content)
                await self.Todo.update_one(
                    {"user": ctx.author.id}, 
                    {"$set": {"todo": items}}
                )
                return await ctx.send(
                    f"Successfully edited to-do index: `{index+1}`\n**content:** `{content}`"
                )
            except IndexError:
                return await ctx.send("Looks like that index doesn't exist on your list!")

            except Exception as e:
                return await ctx.send(
                    f"Oops looks like an error occured registering the todo-item:\n`{e}`\nPlease try again later."
                )

    @todo.command(
        name="info", 
        description="info on todo-item"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx, index: int):
        user = await self.Todo.find_one(
            {"user": ctx.author.id}
        )
        if not user:
            await self.Todo.insert_one(
                {
                    "user": ctx.author.id, "todo": []
                }
            )
            return await ctx.send(
                "You do not have a todo list yet!\nStart by doing `%todo add`"
            )
        else:
            try:
                conv = commands.MessageConverter()
                index -= 1
                item = user["todo"][index]
                created_at = await conv.convert(ctx, item[0])
                created_at = created_at.created_at.strftime(self.PyBot._timeformat)
                embed = discord.Embed(
                    title=f"Todo item `{index}`", 
                    description=f"```ini\n[ Index ] : {index}\n[ Created at ] : {created_at}\n[ Content ] : {item[1]}\n```\n\n[Jump to message]({item[0]})", 
                    timestamp = dt.utcnow()
                )
                embed.set_footer(text=f"{ctx.author.name}'s To-do list", icon_url=ctx.author.avatar_url)
                return await ctx.send(embed=embed)
            except IndexError:
                return await ctx.send("Looks like that index doesn't exist on your list!")

            except Exception as e:
                return await ctx.send(
                    f"Oops looks like an error occured registering the todo-item:\n`{e}`\nPlease try again later."
                )

    @todo.command(
        name="insert",
        description="Inserts a todo item (similar to 'add' but it inserts it into the index position you provide instead of appending it to the end"
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def insert(self, ctx, index: int, *, content: str):
        user = await self.Todo.find_one(
            {"user": ctx.author.id}
        )
        if not user:
            await self.Todo.insert_one(
                {
                    "user": ctx.author.id, "todo": []
                }
            )
            return await ctx.send(
                "You do not have a todo list yet!\nStart by doing `%todo add`"
            )
        if len(content) > 220:
            return await ctx.send("Please keep the to-do content under 220 characters!")
        else:
            try:
                index -= 1
                array = user["todo"]
                array.insert(index, (ctx.message.jump_url, content))
                await self.Todo.update_one(
                    {"user": ctx.author.id}, 
                    {"$set": {"todo": array}}
                )
                return await ctx.send(
                    f"Successfully inserted a new item into index: `{index+1}`\n**content:** `{content}`"
                )
            except IndexError:
                return await ctx.send("Looks like that index doesn't exist on your list!")
            except Exception as e:
                return await ctx.send(
                    f"Oops looks like an error occured registering the todo-item:\n`{e}`\nPlease try again later."
                )

    @todo.command(
        name="swap",
        description="Inserts a todo item (similar to 'add' but it inserts it into the index position you provide instead of appending it to the end"
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def swap(self, ctx, original: int, to: int):
        user = await self.Todo.find_one(
            {"user": ctx.author.id}
        )
        if not user:
            await self.Todo.insert_one(
                {
                    "user": ctx.author.id, "todo": []
                }
            )
            return await ctx.send(
                "You do not have a todo list yet!\nStart by doing `%todo add`"
            )
        else:
            try:
                original -= 1
                to -= 1
                array = user["todo"]
                array[original], array[to] = array[to], array[original]

                await self.Todo.update_one(
                    {"user": ctx.author.id}, 
                    {"$set": {"todo": array}}
                )
                return await ctx.send(
                    f"Successfully swapped index `{original+1}` with `{to+1}`"
                )
            except IndexError:
                return await ctx.send("Looks like that index doesn't exist on your list!")
            except Exception as e:
                return await ctx.send(
                    f"Oops looks like an error occured registering the todo-item:\n`{e}`\nPlease try again later."
                )

def setup(client):
    client.add_cog(ToDoSystem(client))