import aiohttp
from aiohttp import ClientSession
import json
import asyncio
import discord
from datetime import datetime as dt
from discord.ext import commands
from io import BytesIO, StringIO
import time
import markdown
import markdownify

class ApiError(Exception):
    pass

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

        embed = discord.Embed(
            title = f"Code evaluation in  `{raw_lang}`",
            description = f"`INFO: Code evaluated with exit status {status}`",
            color = discord.Color.greyple(),
            timestamp = dt.utcnow()
        )
        head = ">>>" if language in {"python3", "python"} else f'"{language} - {version}"'
        truncated = False
        truncated2 = False

        if len(output) > 1927: truncated = True
        if len(stderr) > 1927: truncated2 = True

        output = output[:(1927 - len(stderr) - len(head))]
        stderr = stderr[:(1927 - len(output) - len(head))]

        if truncated:
            output = output[:-40]
            output += "\n...\nTruncated (output too long)"

        if truncated2:
            stderr = stderr[:-40]
            stderr += "\n...\nTruncated (output too long)"

        MessageString = f'''
```{raw_lang}
{head} [stdout]: 
{output}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{head} [stderr]: 
{stderr}
```
        '''
        return embed, MessageString, status

class Eval(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.languages = {
            "javascript" : "js",
            "java"       : None,
            "c"          : None,
            "cpp"        : "c++",
            "go"         : "golang",
            "csharp"     : "cs",
            "typescript" : "ts", 
            "ruby"       : None,
            "rust"       : None,
            "perl"       : None, 
            "php"        : None, 
            "bash"       : None, 
            "swift"      : None, 
            "kotlin"     : None,
            "brainfuck"  : None, 
            "lua"        : None, 
            "haskell"    : None, 
            "nim"        : None, 
            "dash"       : None, 
            "d"          : None, 
        }

    @commands.command(
        name= "eval", 
        description= "evaluates python code",
        aliases = ["pyeval"],
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def eval(self, ctx, *, code: str):
        start = time.perf_counter()
        if code.startswith("```py"):
            code = code.strip("```py")
            code = code.strip("```")
        elif code.startswith("```"):
            code = code.strip("```")

        session = Piston()
        output = await session.MakeRequest("python", code)
        embed, message, status = await session.parse_request("python", output)

        if status == 0:
            await ctx.message.add_reaction("✅")
        elif status == 1:
            await ctx.message.add_reaction("❌")
        else:
            await ctx.message.add_reaction("⚠️")

        embed.set_footer(text=f"Executed by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        end = time.perf_counter()
        embed.description += f"\n`[Finished in {(end - start):.2f}s]`"
        return await ctx.reply(message, embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(
        name="compile", 
        description="compiles code in other languages specified\nNote: For python code-evaluation please use the eval command instead", 
        aliases=["other"],
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def compile(self, ctx, language: str, *, code: str):

        if language.lower() in {"python", "python3"}:
            return await ctx.send("**For python code-evaluation please use the eval command instead:**\n`%help eval`\n`%eval <code>`")

        if language.lower() not in self.languages and language.lower() not in [self.languages[l.lower()] for l in self.languages]:
            return await ctx.send(
                f'''
**That language is not supported yet! Try one of these:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`{"` `".join(self.languages)}`
                '''
            )

        else:
            start = time.perf_counter()

            if code.startswith("```"):
                lines = code.split("\n")
                if lines[0].startswith("```"):
                    code = code.strip(lines[0])
                    code = code.strip("```")

            session = Piston()
            output = await session.MakeRequest(language, code)
            embed, message, status = await session.parse_request(language, output)

            if status == 0:
                await ctx.message.add_reaction("✅")
            elif status == 1:
                await ctx.message.add_reaction("❌")
            else:
                await ctx.message.add_reaction("⚠️")

            embed.set_footer(text=f"Executed by {ctx.author.name}", icon_url=ctx.author.avatar_url)
            end = time.perf_counter()
            embed.description += f"\n`[Finished in {(end - start):.2f}s]`"
            return await ctx.reply(message, embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name="mdtohtml", description="Converts markdown to html", aliases=["markdowntohtml", "htmlify"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def mdtohtml(self, ctx, *, code: str):

        if code.startswith("```md") or code.startswith("```markdown"):
            lines = code.split("\n")
            code = code.strip(lines[0])
            code = code.strip("```")
        elif code.startswith("```"):
            code = code.strip("```")

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
    async def htmltomd(self, ctx, *, code: str):

        if code.startswith("```html"):
            code = code.strip("```html")
            code = code.strip("```")
        elif code.startswith("```"):
            code = code.strip("```")

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