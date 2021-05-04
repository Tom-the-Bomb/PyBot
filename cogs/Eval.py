import aiohttp
from aiohttp import ClientSession
import json
import asyncio
import discord

from datetime import datetime as dt
from discord.ext import commands
from io import BytesIO, StringIO
from cogs import paste

import time
import markdown
import markdownify

from jishaku import codeblocks

class Piston:
    
    def __init__(self, url = "https://emkc.org/api/v1/piston/"):

        self.api_url = url
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    async def MakeRequest(self, language: str, code: str) -> dict:
        
        payload = json.dumps(
            {
                "source": code, 
                "language": language
            }
        )
        async with ClientSession() as session: 
            async with session.post("https://emkc.org/api/v1/piston/execute", data=payload) as r:
                if r.status == 400:
                    return False
                return await r.json()
    
    async def parse_request(self, raw_lang: str, response: dict):
        _        = response.get("ran")
        language = response["language"]
        version  = response["version"]
        output   = response["output"]
        stdout   = response["stdout"]
        stderr   = response["stderr"]

        output = "" if stderr else output
        status = 1 if stderr else 2 if not stdout else 0
        raw_lang = "python" if raw_lang == "python2" else raw_lang

        embed = discord.Embed(
            title = f"Code evaluation in  `{raw_lang}`",
            description = f"```diff\n+ INFO: Code evaluated with exit status {status}",
            color = discord.Color.greyple(),
            timestamp = dt.utcnow()
        )

        MessageString = f'''
```{raw_lang}
"{language} - {version}"

{stdout or stderr or "[No output]"}
```
        '''
        return embed, MessageString, status

class Eval(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.languages = [
            "bash", "brainfuck", "cjam", 
            "clojure", "coffeescript", "cow", 
            "crystal", "dart", "dash", 
            "deno", "dotnet", "dragon", 
            "elixir", "emacs", "erlang", 
            "gawk", "gcc", "go", 
            "golfscript", "groovy", "haskell", 
            "java", "jelly", "julia", 
            "kotlin", "lisp", "lolcode", 
            "lua", "mono", "nasm", 
            "nim", "node", "ocaml", 
            "osabie", "paradoc", 
            "pascal", "perl", "php", 
            "ponylang", "prolog", "pure", 
            "python", "rockstar", "ruby", 
            "rust", "scala", "swift", 
            "typescript", "vlang", "yeethon", "zig"
        ]

    @commands.command(
        name="eval", 
        description="compiles code in the language specified -> languages include: python, js, c, c++, go and many more", 
        aliases=["compile", "exec", "execute"],
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def compile(self, ctx, language: str, *, code: codeblocks.codeblock_converter):

        code  = code.content
        start = time.perf_counter()

        session = Piston()
        output  = await session.MakeRequest(language, code)

        if not output:
            return await ctx.send(
            f'''
**That language is not supported yet! Try one of these:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`{"` `".join(self.languages)}`
            '''
        )

        embed, message, status = await session.parse_request(language, output)

        if   status == 0:
            await ctx.message.add_reaction("✅")
        elif status == 1:
            await ctx.message.add_reaction("❌")
        else:
            await ctx.message.add_reaction("⚠️")

        embed.set_footer(text=f"Executed by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        end = time.perf_counter()
        embed.description += f"\n- [Finished in {(end - start):.2f}s]\n```"
        try:
            return await ctx.reply(message, embed=embed, allowed_mentions=discord.AllowedMentions.none())
        except discord.HTTPException:
            code   = codeblocks.codeblock_converter(message).content
            paste_ = paste.Paste(ctx.bot)
            paste_ = await paste_.paste_mystbin(code)
            return await ctx.send(f"**The output was too long to be sent**\nI've pasted it externally instead: https://mystb.in/{paste_['pastes'][0]['id']}")

    @commands.command(name="mdtohtml", description="Converts markdown to html", aliases=["markdowntohtml", "htmlify"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def mdtohtml(self, ctx, *, code: codeblocks.codeblock_converter):

        code = code.content

        html = markdown.markdown(code)
        if len(html) > 1980: 
            with StringIO() as stream:
                stream.write(html)
                stream.seek(0)
                return await ctx.send(file=discord.File(stream, "index.html"))
        else:
            return await ctx.send(f"```html\n{html or '-'}\n```")

    @commands.command(name="htmltomd", description="Converts html to markdown", aliases=["htmltomarkdown", "mdify", "markdownify"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def htmltomd(self, ctx, *, code: codeblocks.codeblock_converter):

        code = code.content

        md = markdownify.markdownify(code)
        if len(md) > 1980: 
            with StringIO() as stream:
                stream.write(md)
                stream.seek(0)
                return await ctx.send(file=discord.File(stream, "file.md"))
        else:
            return await ctx.send(f"```md\n{md or '-'}\n```")

def setup(client):
    client.add_cog(Eval(client))