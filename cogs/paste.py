import discord
from discord.ext import commands
import aiohttp
from aiohttp import ClientSession
from datetime import datetime as dt
import json
from io import StringIO

from jishaku import codeblocks

class Paste(commands.Cog):

    def __init__(self, client):
        self.PyBot = client
        self.mystbin_url = "https://mystb.in/api/pastes"
        self.gist_url = "https://api.github.com/gists"

        self.git_key = self.PyBot.config["GITHUB"]["KEY"]

    async def format_extension(self, language):
        conv = {
            "python": "py", 
            "javascript": "js", 
            "c++": "cpp",
            "csharp": "cs",
            "kotlin": "kts", 
            "fsharp": "fs", 
            "rust": "rs", 
            "typescript": "ts", 
            "haskell": "hs", 
            "brainfuck": "bf", 
            "markdown": "md"
        }
        ext = conv.get(language.lower())
        if ext:
            return ext
        else:
            return language.lower()

    async def create_gist(self, ctx, language: str, code: str) -> dict:
        headers = {'Authorization': f"token {self.git_key}"}
        params = {'scope': 'gist'}
        payload = {
            "description": "Automated GIST created through discord",
            "public": True,
            "files": {
                f"{ctx.message.id}.{language}": {
                    "content": code,
                }
            }
        }
        async with ClientSession() as session:
            async with session.post(
                url = self.gist_url, 
                headers = headers, 
                params = params, 
                data = json.dumps(payload)
            ) as r:
                
                if r.status in range(200, 299):
                    return await r.json()

    async def paste_mystbin(self, code: str) -> dict:

        multi_part_write = aiohttp.MultipartWriter()
        paste_content = multi_part_write.append(code)
        paste_content.set_content_disposition("form-data", name="data")
        paste_content = multi_part_write.append_json(
            {"meta": [{"index": 0, "syntax": "python"}]}
        )
        paste_content.set_content_disposition("form-data", name="meta")

        async with ClientSession() as session:
            async with session.post(self.mystbin_url, data=multi_part_write) as r:
                if r.status in range(200, 299):
                    return await r.json()

    @commands.command(
        name="mystbin", 
        aliases=["myst", "mpaste", 'paste'],
        description="Pastes provided code in mystbin and returns the link"
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def mystbin(self, ctx, *, code: codeblocks.codeblock_converter):
        
        code = code.content
            
        res = await self.paste_mystbin(code)
        url = f"https://mystb.in/{res['pastes'][0]['id']}"
        embed = discord.Embed(
            title = "Pasted code | Mystbin.in", 
            description = f"`URL:` {url}",
            url = url,
            timestamp = dt.utcnow(),
        ).set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed)

    @commands.command(
        name="gist",
        description="Creates a github gist with your provided code", 
        aliases=["gistpaste", "gitpaste", "creategist"]
    )
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def gist(self, ctx, *, code: codeblocks.codeblock_converter):
        lang = code.language
        code = code.content

        lang = await self.format_extension(lang)

        res = await self.create_gist(ctx, lang, code)
        embed = discord.Embed(
            title = "New gist created", 
            description = (
                f'''
```ini
[ ID ]       : {res['id']}
[ Type ]     : {res["files"][f"{ctx.message.id}.{lang}"]["type"]}
[ Language ] : {res["files"][f"{ctx.message.id}.{lang}"]["language"]}
```

**[Url to gist]({res['html_url']})**
**[Url to file]({res["files"][f"{ctx.message.id}.{lang}"]["raw_url"]})**
**[Push Url]({res["git_push_url"]})**
**[Pull Url]({res["git_pull_url"]})**
'''
            ), 
            url = res["html_url"], 
            timestamp = dt.utcnow()
        )
        embed.set_footer(text="Created at", icon_url=self.PyBot.user.avatar_url)
        return await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name="save", description="saves your code to a file", aliases=["file"])
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def save(self, ctx, ext: str, *, code: codeblocks.codeblock_converter):

        code = code.content

        with StringIO() as stream:
            stream.write(code)
            stream.seek(0)
            return await ctx.send(file=discord.File(stream, f"index.{ext}"))

def setup(client):
    client.add_cog(Paste(client))