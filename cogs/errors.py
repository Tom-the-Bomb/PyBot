import discord
from discord.ext import commands

class Errorhandler(commands.Cog):

    def __init__(self, client):
        self.PyBot = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, "original", error)

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f'You are missing the `{", ".join(error.missing_perms)}` permissions to do that')

        elif isinstance(error, discord.NotFound):
            await ctx.send('I couldn\'t find what you were looking for...')

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f'I am missing the `{", ".join(error.missing_perms)}` permission!')

        elif isinstance(error, commands.NotOwner):
            await ctx.send('This is an owner only command!')

        elif isinstance(error, commands.UserNotFound):
            await ctx.send(f'I couldn\'t find user: `{error.argument}`, please try again')

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f'I couldn\'t find member: `{error.argument}`, please try again')

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send('I couldn\'t find this channel, please try again')

        elif isinstance(error, commands.RoleNotFound):
            await ctx.send('I couldn\'t find this role, please try again')

        elif isinstance(error, commands.EmojiNotFound):
            await ctx.send('I couldn\'t find this emoji, please try again')

        elif isinstance(error, commands.MessageNotFound):
            await ctx.send('Could not find this message within my cache, please try again')

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f'Missing `{error.param}` argument in the command.\n**Usage:** `%{ctx.invoked_with} {ctx.command.signature}`'
            )

        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid Argument for command!, Do `%help <CommandName> to get the proper usage`")

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'This command is on cooldown please try again after `{round(error.retry_after)}` seconds!')

        elif isinstance(error, discord.Forbidden):
            await ctx.message.add_reaction('❌')

        elif isinstance(error, discord.HTTPException):
            await ctx.message.add_reaction('‼️')

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.NSFWChannelRequired):
            await ctx.send("This command is nsfw only since its a google-image command and google is uh")
            
        else:
            raise error

def setup(client):
    client.add_cog(Errorhandler(client))