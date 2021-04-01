import discord
from discord.ext import commands
from aiohttp import ClientSession

import bs4
from bs4 import BeautifulSoup
import re
import io
import os
import zlib

class SphinxObjectFileReader:

    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode('utf-8')

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b''
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b'\n')
            while pos != -1:
                yield buf[:pos].decode('utf-8')
                buf = buf[pos + 1:]
                pos = buf.find(b'\n')

class DocScraper:

    def __init__(self):

        self.thumbnail = "https://www.pinclipart.com/picdir/big/269-2691398_python-logo-clipart-transparent-background-png-download.png"


    def parse_object_inv(self, stream, url):
        
        result = {}

        inv_version = stream.readline().rstrip()

        if inv_version != '# Sphinx inventory version 2':
            raise RuntimeError('Invalid objects.inv file version.')

        projname = stream.readline().rstrip()[11:]
        __ = stream.readline().rstrip()[11:]

        line = stream.readline()
        if 'zlib' not in line:
            raise RuntimeError('Invalid objects.inv file, not z-lib compatible.')

        entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, __, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(':')
            if directive == 'py:module' and name in result:
                
                continue

            if directive == 'std:doc':
                subdirective = 'label'

            if location.endswith('$'):
                location = location[:-1] + name

            key = name if dispname == '-' else dispname
            prefix = f'{subdirective}:' if domain == 'std' else ''

            if projname == 'discord.py':
                key = key.replace('discord.ext.commands.', '').replace('discord.', '')

            result[f'{prefix}{key}'] = os.path.join(url, location)

        return result

    def finder(self, text, collection, *, key=None, lazy=True):
        suggestions = []
        text = str(text)
        pat = '.*?'.join(map(re.escape, text))
        regex = re.compile(pat, flags=re.IGNORECASE)
        for item in collection:
            to_search = key(item) if key else item
            r = regex.search(to_search)
            if r:
                suggestions.append((len(r.group()), r.start(), item))

        def sort_key(tup):
            if key:
                return tup[0], tup[1], key(tup[2])
            return tup

        if lazy:
            return (z for _, _, z in sorted(suggestions, key=sort_key))
        else:
            return [z for _, _, z in sorted(suggestions, key=sort_key)]

    async def build_rtfm_lookup_table(self, page_types):
        cache = {}
        for key, page in page_types.items():
            async with ClientSession() as session:
                async with session.get(page + '/objects.inv') as resp:
                    if resp.status != 200:
                        raise RuntimeError('Cannot build rtfm lookup table, try again later.')

                    stream = SphinxObjectFileReader(await resp.read())
                    cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    async def do_rtfm(self, ctx, key, obj):
        page_types = {
            'latest': 'https://discordpy.readthedocs.io/en/latest',
            'latest-jp': 'https://discordpy.readthedocs.io/ja/latest',
            'python': 'https://docs.python.org/3',
            'python-jp': 'https://docs.python.org/ja/3',
        }

        if obj is None:
            await ctx.send(page_types[key])
            return

        if not hasattr(self, '_rtfm_cache'):
            await self.build_rtfm_lookup_table(page_types)

        obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)

        if key.startswith('latest'):
            
            q = obj.lower()
            for name in dir(discord.abc.Messageable):
                if name[0] == '_':
                    continue
                if q == name:
                    obj = f'abc.Messageable.{name}'
                    break

        cache = list(self._rtfm_cache[key].items())

        matches = self.finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]

        e = discord.Embed(colour=discord.Colour.gold())
        if len(matches) == 0:
            return await ctx.send('Could not find anything. Sorry.')
        
        e.title = "Python-3 Documentation"
        e.url = "https://docs.python.org/3/"
        e.description = f"**Results for | `{obj}`**\n━━━━━━━━━━━━━━\n"+'\n'.join(f'[`{key}`]({url})' for key, url in matches)
        e.set_thumbnail(url=self.thumbnail)
        await ctx.send(embed=e)

class Documentation(commands.Cog):

    def __init__(self, client):
        self.PyBot = client

    @commands.command(name="docs", description="Quick search in the python-3 docs for the thing you;re looking for")
    async def docs(self, ctx, *, query: str):
        
        docs = DocScraper()
        return await docs.do_rtfm(ctx, "python", query)
            
def setup(client):
    client.add_cog(Documentation(client))