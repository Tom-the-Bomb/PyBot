import discord
from discord.ext import commands, menus
import typing
import textwrap

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from io import BytesIO

import unicodedata
import re
import random

from RevImg import RevImg
import async_cse

class LanguageConv(commands.Converter):
    async def convert(self, ctx, language):
        lang = language.lower()
        conv = {
            "arabic": "ara",
            "bulgarian": "bul",
            "chinese": "chs",
            "croatian": "hrv",
            "czech": "cze",
            "danish": "dan",
            "dutch": "dut",
            "english": "eng",
            "finnish": "fin",
            "french": "fre",
            "german": "ger",
            "greek": "gre",
            "hungarian": "hun",
            "korean": "kor",
            "italian": "ita",
            "japanese": "jpn",
            "polish": "pol",
            "portuguese": "por",
            "russian": "rus",
            "slovenian": "slv",
            "spanish": "spa",
            "swedish": "swe",
            "turkish": "tur",
        }
        if not language:
            return "eng"
        elif lang in conv.values():
            return lang
        else:
            res = "eng" if not conv.get(lang) else conv.get(lang)
            return res

class PaginatorSource(menus.ListPageSource):

    def __init__(self, ctx, entries, *, per_page=1):
        self.ctx = ctx
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        
        owner = page["owner"]
        embed = discord.Embed(
            title = page["title"],
            description = f'''
```ini
 • [ id ] :      {page["question_id"]}
 • [ Views ] :   {page["view_count"]}
 • [ Score ] :   {page["score"]}
 • [ Answers ] : {page["answer_count"]}
 • [ license ] : {page.get("content_license")}
```
**[Click here]({page["link"]})**
**Tags:** `{"` `".join(page.get("tags"))}`
''',
            url = page["link"],
            color = discord.Color.greyple(),
        )
        embed.set_author(name=owner.get("display_name", discord.Embed.Empty), icon_url=owner.get("profile_image", discord.Embed.Empty))
        embed.set_footer(text=f"Requested by {self.ctx.author.name} •  page {menu.current_page+1}/{self.get_max_pages()}", icon_url=self.ctx.author.avatar_url)
        return embed

    def is_paginating(self):
        
        return True

class RepoPaginator(menus.ListPageSource):

    def __init__(self, ctx, entries, *, per_page=1):
        self.ctx = ctx
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        newline = "\n"
        notfound = "https://github.com/404"
        owner = page["owner"]
        embed = discord.Embed(
            title = page["full_name"],
            description = f'''
```ini
 • [ id ]           : {page["id"]}
 • [ Stars ]        : {page["stargazers_count"]}
 • [ Watchers ]     : {page["watchers"]}
 • [ Score ]        : {page["score"]}
 • [ forks ]        : {page["forks"]}
 • [ issues ]       : {page["open_issues"]}
 • [ Language ]     : {page["language"]}
 • [ size ]         : {page["size"]}
 • [ Created-at ]   : {page["created_at"][:10]}
 • [ Last-pushed ]  : {page["pushed_at"][:10]}
 • [ Last-updated ] : {page["updated_at"][:10]}
```
**Description**
{newline.join(textwrap.wrap(page["description"] or "-", width=32))}

━━━━━━━━━━━━━━━━━━━━━━━━
**[clone url]({page["clone_url"] or notfound})**
**[teams url]({page["teams_url"] or notfound})**
**[forks url]({page["forks_url"] or notfound})**
**[homepage]({page["homepage"] or notfound})**
''',
            url = page["html_url"],
            color = discord.Color.greyple(),
        )
        embed.set_author(name=owner["login"], icon_url=owner["avatar_url"])
        embed.set_footer(text=f"Requested by {self.ctx.author.name} •  page {menu.current_page+1}/{self.get_max_pages()}", icon_url=self.ctx.author.avatar_url)
        return embed

    def is_paginating(self):
        
        return True

class UserPaginator(menus.ListPageSource):

    def __init__(self, ctx, entries, *, per_page=1):
        self.ctx = ctx
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        
        notfound = "https://github.com/404"
        embed = discord.Embed(
            title = page["login"],
            description = f'''
```ini
 • [ id ]      : {page["id"]}
 • [ Type ]    : {page["type"]}
 • [ admin? ]  : {page["site_admin"]}
 • [ score ]   : {page["score"]}
 • [ node-id ] : {page["node_id"]}
```
**[Repositories url]({page["repos_url"] or notfound})**
**[followers url]({page["followers_url"] or notfound})**
**[organizations url]({page["organizations_url"] or notfound})**
''',
            url = page["html_url"],
            color = discord.Color.greyple(),
        )
        embed.set_thumbnail(url=page["avatar_url"])
        embed.set_footer(text=f"Requested by {self.ctx.author.name} •  page {menu.current_page+1}/{self.get_max_pages()}", icon_url=self.ctx.author.avatar_url)
        return embed

    def is_paginating(self):
        
        return True

class ImagePaginator(menus.ListPageSource):

    def __init__(self, ctx, entries, *, per_page=1):
        self.ctx = ctx
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        logo = "https://th.bing.com/th/id/R0f1b7e086fcf515daad0de9ecf88de41?rik=kOFIxoLiWIdFFQ&pid=ImgRaw"
        embed = discord.Embed()
        embed.set_image(url=page.image_url)
        embed.set_footer(text=f"Requested by {self.ctx.author.name} •  page {menu.current_page+1}/{self.get_max_pages()}", icon_url=logo)
        return embed

class GooglePaginator(menus.ListPageSource):

    def __init__(self, ctx, entries, *, per_page=1):
        self.ctx = ctx
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        logo = "https://th.bing.com/th/id/R0f1b7e086fcf515daad0de9ecf88de41?rik=kOFIxoLiWIdFFQ&pid=ImgRaw"
        embed = discord.Embed(
            title= page.title, 
            description= page.description, 
            url = page.url, 
            color = discord.Color.gold()
        )
        embed.set_thumbnail(url=page.image_url)
        embed.set_footer(text=f"Requested by {self.ctx.author.name} •  page {menu.current_page+1}/{self.get_max_pages()}", icon_url=logo)
        return embed

class Search(commands.Cog):

    def __init__(self, client):
        self.PyBot       = client
        self.stack_auth  = {
            "access_token": self.PyBot.config["STACKOVERFLOW"]["KEY"]
        }
        self.git_headers = {
            "Authorization": self.PyBot.config["GITHUB"]["SECRET"]
        }
        self.GKeys   = self.PyBot.config["GOOGLE"]
        self.ocr     = self.PyBot.config["OCR"]
        self._google = async_cse.Search([self.GKeys["KEY1"], self.GKeys["KEY2"], self.GKeys["KEY3"], self.GKeys["KEY4"], self.GKeys["KEY5"]])
        self.pep_url    = "https://www.python.org/dev/peps/"
        self.github_url = "https://api.github.com/"
        self.stack_url  = "https://api.stackexchange.com/2.2/"
        self.pypi_logo  = "https://cdn.discordapp.com/attachments/381963689470984203/814267252437942272/pypi.png"
        self.pep_image  = "https://www.python.org/static/opengraph-icon-200x200.png"

    @commands.command(name="pypi", description="searches pypi.org for a package")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def pypi(self, ctx, *, package: str):

        async with ClientSession() as session:
            async with session.get(f'https://pypi.org/pypi/{package}/json') as r:
                notfound = "https://pypi.org/404"
                if r.status in range(200, 299):
                    data = await r.json()
                    data = data['info']

                    download = data.get("download_url")
                    urls = data["project_urls"]
                    docs = urls.get("Documentation") if urls else None
                    home = urls.get("Homepage") if urls else None
                    issue = urls.get("Issue tracker") if urls else None

                    embed = discord.Embed(
                        title = f"{data['name']} | {data['version'] or '-'}", 
                        description = (
                        f'''
{data["summary"]}
```ini
• [ Author ]          : {data['author'] or "UNKNOWN"}\t
• [ Author-Email ]    : {data['author_email'] or "UNKNOWN"}\t
• [ Keywords ]        : {data['keywords'] or "UNKNOWN"}\t
• [ Requires-python ] : {data['requires_python'] or "N/A"}\t
• [ License ]         : {data['license'] or "UNKNOWN"}\t
```
**[Download URL]({(download if download != "UNKNOWN" else notfound) or notfound})**
**[Documentation URL]({(docs if docs != "UNKNOWN" else notfound) or notfound})**
**[Homepage]({(home if home != "UNKNOWN" else notfound) or notfound})**
**[Issues]({(issue if issue != "UNKNOWN" else notfound) or notfound})**
                        '''
                        ),
                        url = data["package_url"],
                        color=discord.Color.gold()
                    )
                    return await ctx.send(embed=embed)
                elif r.status == 404:
                    return await ctx.send(f"This package does not exist!")
                else:
                    return await ctx.send(f"An error has occured...")

    @commands.command(name="stack", aliases=["stacksearch"], description="Does a quick search on stack-overflow based on your query")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stack(self, ctx, *, query: str):

        endpoint = "search"
        params = {
            "order": "desc", 
            "intitle": query, 
            "sort": "activity",
            "site": "stackoverflow"
        }

        async with ClientSession() as session:
            async with session.get(self.stack_url + endpoint, headers=self.stack_auth, params=params) as r:

                if r.status in range(200, 299):
                    data = await r.json()
                    data = data["items"]

                    if len(data) == 0:
                        return await ctx.send("No results were found")

                    if len(data) > 10:
                        data = data[:10]

                    pages = PaginatorSource(ctx=ctx, entries=data)
                    paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)
                    return await paginator.start(ctx)

                elif r.status == 404:
                    return await ctx.send("No results were found")
                else:
                    return await ctx.send("Oops an error has occured")

    @commands.group(
        name= "gitsearch", 
        aliases= ["githubsearch", "github"], 
        invoke_without_command=True, 
        description=r'''
        Searches for repositories on github with your query.
        ex: %gitsearch chessbot
        Has a 'user' subcommand for searching for users instead, 
        You can invoke that with ex: %gitsearch user rapptz
        '''
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def gitsearch(self, ctx, *, query: str):

        endpoint = f"search/repositories"

        async with ClientSession() as session:
            async with session.get(self.github_url + endpoint, headers=self.git_headers, params={"q": query}) as r:

                if r.status in range(200, 299):
                    data = await r.json()
                    data = data["items"]

                    if len(data) == 0:
                        return await ctx.send("No results were found")

                    if len(data) > 10:
                        data = data[:10]

                    pages = RepoPaginator(ctx=ctx, entries=data)
                    paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)
                    return await paginator.start(ctx)
                        
                elif r.status == 404:
                    return await ctx.send("No results were found")
                else:
                    return await ctx.send("Oops an error has occured")

    @gitsearch.command(name="user", description="Searches on github for users")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def user(self, ctx, *, query: str):

        endpoint = f"search/users"

        async with ClientSession() as session:
            async with session.get(self.github_url + endpoint, headers=self.git_headers, params={"q": query}) as r:

                if r.status in range(200, 299):
                    data = await r.json()
                    data = data["items"]

                    if len(data) == 0:
                        return await ctx.send("No results were found")

                    if len(data) > 10:
                        data = data[:10]

                    pages = UserPaginator(ctx=ctx, entries=data)
                    paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)
                    return await paginator.start(ctx)
                        
                elif r.status == 404:
                    return await ctx.send("No results were found")
                else:
                    return await ctx.send("Oops an error has occured")

    @commands.command(name="pep", description="Provides informataion on a PEP number")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def pep(self, ctx, *, number: int):
        num = str(number)
        url = self.pep_url + f"pep-{'0'*(4-len(num))}" + num

        async with ClientSession() as session:
            async with session.get(url) as r:

                if r.status in range(200, 299):
                    data = await r.text(encoding="utf-8")
                    
                    def ParsePEP(data):
                        sep  = ("\n", "\n+ ")
                        soup = BeautifulSoup(data, "html.parser")

                        td   = soup.find_all('tr', class_ = "field")
                        th   = [item.th.contents[0] for item in td if item.th.contents]
                        tr   = [item.td.contents[0] for item in td if item.td.contents]

                        desc = "```diff\n"
                        for a, b in zip(th, tr):
                            if hasattr(b, "contents"):
                                desc += f"- [ {a} ]\n+ {b.contents[0].replace(*sep)}\n"
                            else:
                                desc += f"- [ {a} ]\n+ {b.replace(*sep)}\n"
                        desc += "\n```"

                        embed = discord.Embed(
                            title = soup.title.contents[0],
                            url   = url,
                            description = desc,
                        )
                        embed.set_thumbnail(url=self.pep_image)
                        return embed

                    embed = await self.PyBot.loop.run_in_executor(None, ParsePEP, data)
                    return await ctx.send(embed=embed)

                elif r.status == 404:
                    return await ctx.send("That PEP does not exist!")

    @commands.command(name="char", aliases=["charinfo", "unicode"], description="Unicode character info")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def char(self, ctx, *, characters: str):

        custom_emoji = re.match(r"<(a?):(\w+):(\d+)>", characters)
        if custom_emoji:
            return await ctx.send("Custom emojis are not allowed...")
        if len(characters) > 25:
            return await ctx.send("Please keep the character length under 25...")

        def get_info(char: str):
            digit = f"{ord(char):x}"
            if len(digit) <= 4:
                u_code = f"\\u{digit:>04}"
            else:
                u_code = f"\\U{digit:>08}"

            url = f"https://www.compart.com/en/unicode/U+{digit:>04}"
            name = f"**[{unicodedata.name(char, '')}]({url})**"

            info = f"`{u_code.ljust(10).replace(' ', '')}` | {name}\t•\t**{discord.utils.escape_markdown(char)}**"
            return info, u_code

        char_list, raw_list = zip(*(get_info(c) for c in characters))
        embed = discord.Embed(title="Unicode Character Info Engine")
        embed.description = "\n".join(char_list) + "\n\u200b"
        embed.add_field(name='Full Raw Text', value=f"`{''.join(raw_list)}`", inline=False)
        
        return await ctx.send(embed=embed)

    @commands.command(name="revimg", aliases=["reverseimgsearch", "revimgsearch"], description="Reverse image searches with an image url you provide")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def revimg(self, ctx, *, url: str):
        r = RevImg()
        try:
            r = r.get_best_guess(url)
        except:
            return await ctx.send("no results were found")
        return await ctx.reply(
            embed = discord.Embed(
                title="Reverse image search result",
                description=f"`{r}`"
            ), 
            allowed_mentions= discord.AllowedMentions.none()
        )

    @commands.command(name="image", description="Performs a google image search with your inputted query")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_nsfw()
    async def image(self, ctx, *, query: str):

        try:
            results = await self._google.search(
                query = query, 
                safesearch = False, 
                image_search = True
            )
            pages = ImagePaginator(ctx=ctx, entries=results)
            paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)
            return await paginator.start(ctx)

        except async_cse.NoResults:
            embed = discord.Embed(description='No results were found for that query... :(')
            return await ctx.send(embed=embed)

    @commands.command(name="google", description="Performs a google query search with your inputted query", aliases=["search"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def google(self, ctx, *, query: str):

        try:
            results = await self._google.search(
                query = query, 
                safesearch = True if not ctx.channel.is_nsfw() else False, 
                image_search = False
            )
            pages = GooglePaginator(ctx=ctx, entries=results)
            paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)
            return await paginator.start(ctx)

        except async_cse.NoResults:
            embed = discord.Embed(description='No results were found for that query... :(')
            return await ctx.send(embed=embed)

    @commands.command(
        name        = "imagetotext", 
        aliases     = ["ocr"], 
        description = "Extracts text from a provided image\n(if the text in an image is a different language you can specify the language after the url and it will detect text in that language and not english)"
    )
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def imagetotext(self, ctx, url: str, lang: typing.Optional[LanguageConv] = "eng"):

        if not url.startswith("https://") and not url.startswith("http://"):
            return await ctx.send("urls must start with http or https.")

        else:
            key = self.ocr[random.choice(("KEY", "KEY2"))]
            async with ClientSession() as session:
                async with session.get("https://api.ocr.space/parse/imageurl", params={"apikey": key, "url": url, "language": lang}) as r:
                    if r.status in range(200, 299):
                        data = await r.json()
                        return await ctx.send(f'```\n{data["ParsedResults"][0]["ParsedText"] or "[Nothing was found]"}\n```')
                    else:
                        return await ctx.send(r.status)

    @commands.command(name="http")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def _http(self, ctx, status_code: int):
        async with ClientSession() as session:
            async with session.get(f"https://http.cat/{status_code}") as r:
                if r.status in range(200, 299):
                    return await ctx.send(
                        file = discord.File(
                            fp = BytesIO(await r.read()),
                            filename = "http.png"
                        )
                    )
                elif r.status == 404:
                    return await ctx.send("Invalid status code")
                else:
                    return await ctx.send("Oops an error occured")

    @commands.command(name="weather")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def weather(self, ctx, *, location: str):
        async with ClientSession() as session:
            async with session.get("https://api.cool-img-api.ml/weather-card", params={"location": location}) as r:
                if r.content_type == "image/png":
                    return await ctx.reply(
                        file = discord.File(
                            fp = BytesIO(await r.read()),
                            filename = "weather.png"
                        ),
                        allowed_mentions = discord.AllowedMentions.none()
                    )
                else:
                    return await ctx.send("Unknown Location or server-error")
            
def setup(client):
    client.add_cog(Search(client))