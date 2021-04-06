import discord
from discord import PublicUserFlags as Flags
from discord.ext import commands, menus, tasks
from datetime import datetime as dt
import re

import pyshorteners
import json


time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    
    async def convert(self, ctx, argument):
        
        matches = time_regex.findall(argument.lower())
        if not matches:
            raise commands.BadArgument('no matches were found')
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument('The supported suffixes for tempmute are `s`, `m`, `h`, and `d`, please try again')
            except ValueError:
                raise commands.BadArgument(f"{v} is not a number!")
        return time

class HelpPaginator(menus.ListPageSource):

    def __init__(self, ctx, bot, entries, *, per_page=1):
        self.ctx = ctx
        self.PyBot = bot
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        
        embed = discord.Embed(
            title = "Commands Help!",
            description = "Type `%help [command]` to get more info on a certain command\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + page,
            color = discord.Color.purple(),
            timestamp = dt.utcnow(),
        )
        embed.set_thumbnail(url=self.PyBot.user.avatar_url)
        embed.set_footer(
            text=f"Requested by {self.ctx.author.name} •  page {menu.current_page+1}/{self.get_max_pages()}", 
            icon_url=self.ctx.author.avatar_url,
        )
        return embed

class Utility(commands.Cog):

    def __init__(self, client):
        self.PyBot = client
        self.hidden_commands = {"load", "unload", "reload", "jishaku"}
        self.hidden_cogs = {"Errorhandler", "Developer", "Jishaku"}

    async def num_status(self, guild):

        online, idle, dnd, offline = 0, 0, 0, 0
        for member in guild.members:
            if member.status is discord.Status.online:
                online += 1
            elif member.status is discord.Status.idle:
                idle += 1
            elif member.status is discord.Status.dnd:
                dnd += 1
            elif member.status is discord.Status.offline:
                offline += 1
        return online, idle, dnd, offline

    @commands.command(
        name="help", 
        description="Help command to provide information on command usage and description"
    )
    async def help(self, ctx, *, command: str = None):

        if not command:
            sep = '\n- '
            description = [
                f"**{cog.qualified_name}**" + f"```diff\n- {sep.join([c.qualified_name for c in cog.walk_commands()])}\n```" for cog in [
                    self.PyBot.get_cog(c) for c in self.PyBot.cogs if c not in self.hidden_cogs
                ]
            ]
            pages = HelpPaginator(ctx, bot=self.PyBot, entries=description)
            paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)
            return await paginator.start(ctx)

        raw = command
        command = self.PyBot.get_command(command)
        if command:
            embed = discord.Embed(
                title = "%" + command.qualified_name,
                description = f'''
**Usage** 
```powershell\n%{command.qualified_name} {command.signature}\n```
**Aliases**
`{", ".join(command.aliases) if command.aliases else "no aliases"}`
''', 
                color = discord.Color.gold()
            )
            embed.add_field(
                name = "━━━━━ Description ━━━━━", 
                value = command.description or "-"
            )

            if isinstance(command, commands.Group):
                embed.add_field(name="Subcommands", value=" • " + "\n • ".join([c.qualified_name for c in command.commands]), inline=False)

            embed.set_footer(
                text="[ ]  is optional and < > is required", icon_url=self.PyBot.user.avatar_url
            )
            return await ctx.send(embed=embed)
        else:
            return await ctx.send(f"Command `{raw}` was not found")

    @commands.command(name="info", description="Provides some info and stats on the bot")
    async def info(self, ctx):

        d, h, m, s = await self.PyBot.uptime()
        embed = discord.Embed(
            title='Info', 
            description=f'''
PyBot • bot v1.2
━━━━━━━━━━━━━━
    • Owner: `🐡Tσɱ ƚԋҽ BσɱႦ🦈 #7121`
    • Language: `Python 3.8.7`
    • Library: `Discord.py {discord.__version__}`
    • Uptime: `{d} days, {h} hrs, {m} mins, {s} sec`
    • WS latency: `{round(self.PyBot.latency*1000)} ms`
    • Cogs: `{len(self.PyBot.cogs)}`
━━━━━━━━━━━━━━
**[Website](https://tom-the-bomb.github.io/PyBot-website/)** | **[Invite](https://dsc.gg/pybot)**
            ''', 
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=self.PyBot.user.avatar_url)
        embed.add_field(name='👤 - Members -', value=await self.PyBot.NumMembers(), inline=False)
        embed.add_field(name='🏠 - Server count - ', value=len(self.PyBot.guilds), inline=False)
        embed.add_field(name='📨 - Command Count - ', value=len([c for c in self.PyBot.walk_commands() if c.cog.qualified_name not in self.hidden_cogs]), inline=False)
        return await ctx.send(embed=embed)

    
    @commands.command(name="ping", description="Sends the bot's latency")
    async def ping(self, ctx):
        return await ctx.send(f"**WS-Latency:** `{round(self.PyBot.latency*1000)}.0 ms`")

    @commands.command(name="uptime", description="shows the bot's uptime")
    async def uptime(self, ctx):
        d, h, m, s = await self.PyBot.uptime()
        return await ctx.send(f"**Uptime:** `{d} days, {h} hrs, {m} mins, {s} sec`")
    
    @commands.command(name="avatar", aliases=["pfp", "av"], description="shows a member's avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        a = member.avatar_url_as(format="webp", size=1024)
        b = member.avatar_url_as(format="jpg", size=1024)
        c = member.avatar_url_as(format="png", size=1024)

        embed = discord.Embed(
            title=f"{member}'s avatar",
            description=f"**[WEBP]({a}) | [JPG]({b}) | [PNG]({c})**",
            color = member.color,
            timestamp = dt.utcnow(),
        )
        embed.set_image(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        return await ctx.send(embed=embed)

    @commands.command(name="Guildinfo", aliases = ['gi', 'serverinfo', 'si'], description="Shows some info about the server")
    @commands.cooldown(1, 3, commands.BucketType.channel)
    async def Guildinfo(self, ctx):

        online, idle, dnd, offline = await self.num_status(ctx.guild)
        embed = discord.Embed(title=ctx.guild.name, description=ctx.guild.description, color=discord.Color.blurple())
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name='Owner', value=f'{ctx.guild.owner.name} #{ctx.guild.owner.discriminator}')
        embed.add_field(name='member Count', value=ctx.guild.member_count, inline=False)
        embed.add_field(name='💳 Created on', value=ctx.guild.created_at.strftime("%Y-%m-%d"), inline=False)
        embed.add_field(name='💬  Text channels', value=len(ctx.guild.text_channels))
        embed.add_field(name='🔊  Voice channels', value=len(ctx.guild.voice_channels))
        embed.add_field(name='🗃️ Categories', value=len(ctx.guild.categories))
        embed.add_field(
            name='~ Statuses ~', value=
            f'''<:online:824369025584201729> {online}
            <:idle:824369420058099732> {idle}
            <:dnd:824369429395275837> {dnd}
            <:offline:824369439667519529> {offline}
            \u200b'''
        )
        embed.add_field(name='☑️  Verification', value=ctx.guild.verification_level, inline=True)
        embed.add_field(name='🌏  Region', value=ctx.guild.region)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)

        return await ctx.send(embed=embed)

    @commands.command(name="invite", description="Invite the bot to your server!")
    async def invite(self, ctx):

        embed = discord.Embed(
            title = "Invite the bot to your server!", 
            description = "**[Invite Url](https://dsc.gg/pybot)**", 
            color = discord.Color.gold(), 
            timestamp = dt.utcnow(),
        )
        embed.set_thumbnail(url=self.PyBot.user.avatar_url)
        return await ctx.send(embed=embed)

    @commands.command(name="support", aliases=["supportserver"], description="The bot's support server!")
    async def support(self, ctx):

        embed = discord.Embed(
            title = "Join our support server!",
            description = "**[Click here to join](https://discord.com/invite/gq7WpymjaH)**",
            color = discord.Color.blurple(),
            timestamp = dt.utcnow(),
        )
        return await ctx.send(embed=embed)

    @commands.command(
        name="userinfo", 
        description="Provides info on a user", 
        aliases = ["ui", "whois", "profile"]
    )
    async def userinfo(self, ctx, member: discord.Member = None):
        m = member or ctx.author
        conv = {
            'hypesquad_bravery'   : "<:bravery:826088806787973131>", 
            'hypesquad_balance'   : "<:balance:826088836043636746>", 
            'hypesquad_brilliance': "<:brilliance:826087059306709003>", 
            'early_supporter'     : "<:supporter:826088864821149696>", 
            'verified_bot_developer': "<:VerifiedDeveloper:726578447232532530>", 
            'partner'             : "<:partner:826090409074622464>", 
            'staff'               : "<:staff:826091741509320764>", 
            'bug_hunter'          : "<:bughunter:826092076630016050>", 
            'bug_hunter_level_2'  : "<:bughunter2:826092998860472370>",
            'verified_bot'        : "<:verified:826092596798423070>", 
            'system'              : "<:system:826093796559159336>",
        }
        status = {
            discord.Status.online:'<:status_online:596576749790429200>', 
            discord.Status.offline:'<:status_offline:596576752013279242>', 
            discord.Status.dnd:'<:status_dnd:596576774364856321>', 
            discord.Status.idle:'<:status_idle:596576773488115722>'
        }
        badges = [conv[flag[0]] for flag in m.public_flags if flag[1] and flag[0] != "team_user"]
        roles = [role.mention for role in m.roles[1:]]
        boost = "<:booster:826088855840620584>" if m.premium_since else ""
        nitro = "<:nitro:826088845735886848>" if m.is_avatar_animated() else ""
        bot = "<:bot:826535132848193556>" if m.bot else ""
        embed = discord.Embed(
            title = str(m), 
            description = (
                f'''
{" ".join(badges)} {boost} {nitro} {bot} {status[m.status]}
━━━━━━━━━━━━━━━━━━━━
```ini
 • [ ID ]             : {m.id}
 • [ Joined-server ]  : {m.joined_at.strftime(self.PyBot._timeformat)}
 • [ Created-acc ]    : {m.created_at.strftime(self.PyBot._timeformat)}
 • [ Bot-acc ]        : {m.bot}
 • [ Client ]         : {'desktop' if not m.is_on_mobile() else 'mobile'}
 • [ Color ]          : Hex - {str(m.color).replace("#", "")}
 • [ mutual-servers ] : {len(m.mutual_guilds)}
 • [ Status ]         : {m.status}
 • [ Top-role ]       : {m.top_role.name} ```
**━━━━━━━━\tRoles\t━━━━━━━━**
{"  •  ".join(roles)}
                '''
            ), 
            color = m.color
        )
        embed.set_thumbnail(url=m.avatar_url)
        embed.set_footer(text=f"Guild: {m.guild.name}", icon_url=m.guild.icon_url)
        return await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name="vote", description="vote for me!", aliases=["botlists"])
    async def vote(self, ctx):
        embed = discord.Embed(title="Vote for me!")
        embed.description = (
            "**[discord.ly](https://discord.ly/pybot)**\n"
            "**[botsfordiscord](https://botsfordiscord.com/bot/819345387524456468)**\n"
            "**[Top.gg](https://top.gg/bot/819345387524456468)**\n"
        )
        return await ctx.send(embed=embed)

    @commands.command(name="reminder", aliases=["remind"], description="sets a reminder for you")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reminder(self, ctx, time: TimeConverter, *, content: str):

        raw_time = ctx.message.content.split(" ")[1].lower()
            
        await ctx.reply(f'Reminder has been set for `{raw_time}`')

        async def loopy():
            if not l._current_loop:
                return
            await ctx.send(f'**Reminder:**  {ctx.author.mention}', embed = discord.Embed(description=content + f"\n\n[Jump to message]({ctx.message.jump_url})"))

        l = tasks.Loop(loopy, seconds=time, count=2, minutes=0, hours=0, reconnect=True, loop=None)
        l.start()

    @commands.command(name="shortenurl", description="Returns a tinyurl link that leads to your link provided", aliases=["tinyurl"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def shortenurl(self, ctx, *, url: str):
        try:
            shorten = pyshorteners.Shortener()
            link = shorten.tinyurl.short(url)
        except Exception as e:
            return await ctx.send(f"An error has occured:\n`{e}`")
        return await ctx.reply(embed= discord.Embed(
            description=f"**Shortened url:**\n{link}", 
        ), 
        allowed_mentions= discord.AllowedMentions.none()
        )

    @commands.command(name="pprint", description="pretty-formats JSON", aliases=["prettyprint"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def pprint(self, ctx, *, code: str):

        if code.startswith("```"):
            lines = code.split("\n")
            if lines[0].startswith("```"):
                code = code.strip(lines[0])
                code = code.strip("```")
        
        j = json.loads(code)
        j = json.dumps(j, indent=4, sort_keys=True)
        return await ctx.send(f"```json\n{j or '-'}\n```")

def setup(client):
    client.add_cog(Utility(client))