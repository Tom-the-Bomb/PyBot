import discord
from discord.ext import commands
from doc_search import AsyncScraper


class Docs:
    __slots__ = ("url", "aliases")

    def __init__(self, *, url: str, aliases: tuple = ()):
        self.url = url
        self.aliases = aliases

class Documentation(commands.Cog):

    def __init__(self, client):
        self.PyBot    = client
        self.scraper  = AsyncScraper()
        self.page_types = {
            "discord.py": Docs(
                url="https://discordpy.readthedocs.io/en/latest",
                aliases=("d.py", "dpy", "discordpy", "discord"),
            ),
            "python": Docs(
                url="https://docs.python.org/3",
                aliases=("py", "p"),
            ),
            "pillow": Docs(
                url="https://pillow.readthedocs.io/en/stable",
                aliases=("pil",),
            ),
            "asyncpg": Docs(
                url="https://magicstack.github.io/asyncpg/current",
            ),
            "aiohttp": Docs(
                url="https://docs.aiohttp.org/en/stable",
            ),
            "wand": Docs(
                url="https://docs.wand-py.org/en/0.6.5",
            ),
            "numpy": Docs(
                url="https://numpy.org/doc/1.20",
                aliases=('np',),
            ),
            "beautifulsoup": Docs(
                url="https://www.crummy.com/software/BeautifulSoup/bs4/doc",
                aliases=('bs4', 'beautifulsoup4'),
            ),
            "flask": Docs(
                url="https://flask.palletsprojects.com/en/1.1.x",
            ),
            "pymongo": Docs(
                url="https://pymongo.readthedocs.io/en/stable",
                aliases=("mongo",)
            ),
            "yarl": Docs(
                url="https://yarl.readthedocs.io/en/latest",
            ),
            "requests": Docs(
                url="https://docs.python-requests.org/en/master",
            ),
            "selenium-py": Docs(
                url="https://www.selenium.dev/selenium/docs/api/py",
                aliases=('selenium-python', 'selenium')
            ),
            "pandas": Docs(
                url="https://pandas.pydata.org/pandas-docs/stable",
                aliases=("pd",)
            ),
            "pygame": Docs(
                url="https://www.pygame.org/docs",
            ),
            "matplotlib": Docs(
                url="https://matplotlib.org/stable",
                aliases=("mpl",)
            ),
            "sqlalchemy": Docs(
                url="https://docs.sqlalchemy.org/en/14",
            ),
            "wavelink": Docs(
                url="https://wavelink.readthedocs.io/en/latest/", 
            ),
            "motor": Docs(
                url="https://motor.readthedocs.io/en/stable/", 
            ),
            "praw": Docs(
                url="https://praw.readthedocs.io/en/latest/", 
            ),
            "twitchio": Docs(
                url="https://twitchio.readthedocs.io/en/latest/",  
                aliases=("twitch",)
            ),
            "ipython": Docs(
                url="https://ipython.readthedocs.io/en/stable/",  
            ), 
            "sympy": Docs(
                url="https://docs.sympy.org/latest/",   
            ), 
            "scipy": Docs(
                url="https://docs.scipy.org/doc/scipy/reference", 
            ),
            "opencv": Docs(
                url="https://opencv-python.readthedocs.io/en/latest/", 
                aliases=("cv", "cv2")
            ),
            "c": Docs(
                url="c", 
                aliases=("clang")
            ),
            "cpp": Docs(
                url="cpp", 
                aliases=("cplusplus", "c++")
            )
        }

    @commands.group(
        name = "docs", 
        description = r'''
        Quick search in the python-3 or a library docs for the thing you're looking for.
        Optional argument: [library] to search in a lib-docs instead of python
        • Python docs : `%docs py str.split` | `%docs print`
        • Library docs: `%docs requests get` | `%docs dpy ctx.send`...
        ''', 
        invoke_without_command = True, 
        aliases = ["doc", "documentation", "rtfm", "rtfd"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _docs(self, ctx, library_or_lang: str, *, query: str):
        page_ = library_or_lang.lower()
        page  = self.page_types.get(page_)

        if not page:
            matches = [d for d in self.page_types.values() if page_ in d.aliases]
            if not matches:
                return await ctx.send(
                    f'''
**That  [language | library] is not supported yet! Try one of these:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`{"` `".join(self.page_types)}`
                    '''
                )
            page = matches[0]
        page = page.url

        if page == "c":
            matches = await self.scraper.search_c(query)
        elif page == "cpp":
            matches = await self.scraper.search_cpp(query)
        else:
            matches = await self.scraper.search(query, page=page)

        if not matches:
            return await ctx.send('No matches were found...')

        embed = discord.Embed(colour=discord.Colour.gold())
        embed.title = f'{library_or_lang} Documentation'
        embed.url   = matches[0][1]
        embed.description = f"**Results for | `{query}`**\n━━━━━━━━━━━━━━\n"+'\n'.join(f'[`{key}`]({url})' for key, url in matches[:10])
        await ctx.send(embed=embed)

    @_docs.command(name="list")
    async def _list(self, ctx):
        return await ctx.send(
            f'''
**Heres a list of all the available RTFM page types**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`{"` `".join(self.page_types)}`
            '''
        )

def setup(client):
    client.add_cog(Documentation(client))