import discord
from discord.ext import commands

import random
import asyncprawcore
import asyncpraw

class reddit(commands.Cog):
    def __init__(self, client):
        self.PyBot = client
        self.reddit_config = self.PyBot.config["REDDIT"]
        self.reddit = asyncpraw.Reddit(

            client_id     = self.reddit_config["ID"],
            client_secret = self.reddit_config["SECRET"],
            password      = self.reddit_config["PASSWORD"], 
            user_agent    = self.reddit_config["AGENT"], 
            username      = self.reddit_config["USERNAME"],
        )
        self.base = "https://reddit.com"
        self.imgur = 'https://i.imgur.com/'

    @commands.command(
        name="progmeme", 
        aliases = ['progmemes', 'codingmemes', 'codingmeme'],
        description = "Sends a programming meme from reddit\n\\*insert laugh here\\*",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def progmeme(self, ctx):

        memes = ("ProgrammerHumor", "programmingmemes")
        subreddit = await self.reddit.subreddit(random.choice(memes), fetch=True)
        submission = await subreddit.random()

        if submission.is_video:
            return await ctx.send(f'**{submission.title}**\n{submission.url}')

        embed = discord.Embed(title=submission.title, color=discord.Color.red())
        await submission.author.load()
        embed.set_author(name=submission.author.name or "", icon_url=submission.author.icon_img or "")
        embed.url = self.base + submission.permalink
        embed.set_footer(text=f'👍 {submission.score}  |  💬 {submission.num_comments}')

        if 'i.redd.it' in submission.url or self.imgur in submission.url:
            embed.set_image(url=submission.url)
            return await ctx.send(embed=embed)
           
        else:

            if len(submission.selftext) > 2048:
                embed.description = f'{submission.selftext[0:2045]}\n...'
                return await ctx.send(embed=embed)
            else:
                embed.description = f'{submission.selftext}'
                return await ctx.send(embed=embed)

    @commands.command(
        name="python", 
        aliases = ["reddit", "py"],
        description = "Sends posts from r/python",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def python(self, ctx):

        subreddit = await self.reddit.subreddit("python", fetch=True)
        submission = await subreddit.random()

        if submission.is_video:
            return await ctx.send(f'**{submission.title}**\n{submission.url}')

        embed = discord.Embed(title=submission.title, color=discord.Color.red())
        await submission.author.load()
        embed.set_author(name=submission.author.name or "", icon_url=submission.author.icon_img or "")
        embed.url = self.base + submission.permalink
        embed.set_footer(text=f'👍 {submission.score}  |  💬 {submission.num_comments}')

        if 'i.redd.it' in submission.url or self.imgur in submission.url:
            embed.set_image(url=submission.url)
            return await ctx.send(embed=embed)
           
        else:

            if len(submission.selftext) > 2048:
                embed.description = f'{submission.selftext[0:2045]}\n...'
                return await ctx.send(embed=embed)
            else:
                embed.description = f'{submission.selftext}'
                return await ctx.send(embed=embed)
        
def setup(client):
    client.add_cog(reddit(client))