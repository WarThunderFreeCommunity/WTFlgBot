import asyncio
from contextlib import contextmanager
import logging

import aeval
import nextcord
from nextcord.ext import commands

import configuration
from src.extensions.EXFormatExtension import format_exception
from src.extensions.DBWorkerExtension import DataBase

class DeleteMessage(nextcord.ui.View):
    def __init__(self, *, message, ctx):
        """_summary_

        Args:
            message (_type_): _description_
            ctx (_type_): _description_
        """
        super().__init__(timeout=60*5)
        self.message = message
        self.ctx = ctx
    
    @nextcord.ui.button(label="delete this message", style=nextcord.ButtonStyle.grey)
    async def delete_this(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """_summary_

        Args:
            button (nextcord.ui.Button): _description_
            interaction (nextcord.Interaction): _description_
        """
        if self.ctx.author.id  == interaction.user.id:
            await interaction.message.delete()
    
    @nextcord.ui.button(label="delete two messages", style=nextcord.ButtonStyle.grey)
    async def delete_two(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """_summary_

        Args:
            button (nextcord.ui.Button): _description_
            interaction (nextcord.Interaction): _description_
        """
        if self.ctx.author.id == interaction.user.id:
            await self.ctx.message.delete()
            await interaction.message.delete()  

    async def on_timeout(self):
        self.delete_this.disabled = True
        self.delete_two.disabled = True
        try:
            await self.message.edit(view=self)     
        except BaseException:
            pass


class Bot(commands.Bot):
    def __init__(self, cogs_add_on_ready=None, command_prefix=None, help_command=None, intents=None):
        """_summary_

        Args:
            cogs_add_on_ready (_type_, optional): _description_. Defaults to None.
            command_prefix (_type_, optional): _description_. Defaults to None.
            help_command (_type_, optional): _description_. Defaults to None.
            intents (_type_, optional): _description_. Defaults to None.
        """
        super().__init__(command_prefix=command_prefix, help_command=help_command, intents=intents)
        self.DATA: dict = {
            'bot-started': False,
            'messages': {
                "pymsg": None
            }
        }
        self.OWNERS: list[int] = [ # admin + junior admin + moders
            286914074422280194,
            1120793294931234958,
            404512224837894155,
            
        ]
        self.EVAL_OWNER: list[int] = [ # moders
            286914074422280194,
            1120793294931234958,
            404512224837894155,

        ]
        self.cogs_add_on_ready = cogs_add_on_ready

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})\n------")
        if not self.DATA['bot-started']:
            if self.cogs_add_on_ready:
                [self.load_extension(f"src.cogs.{cog}") for cog in self.cogs_add_on_ready]
            application_info = await self.application_info()
            self.OWNERS.append(application_info.owner.id)
            self.EVAL_OWNER.append(application_info.owner.id)
            self.DATA['bot-started'] = True


bot: commands.Bot = Bot(
    cogs_add_on_ready=configuration.cogs_add_on_ready,
    intents=nextcord.Intents.all(),
    command_prefix='>',
    help_command=None,
    )


@bot.command()
async def cog_load(ctx: commands.Context, cog: str):
    """_summary_

    Args:
        ctx (commands.Context): _description_
        cog (str): _description_
    """
    if ctx.author.id not in bot.OWNERS:
        return
    try:
        bot.load_extension(f"src.cogs.{cog}")
    except BaseException as ex:
        message = await ctx.channel.send(f"Exception:\n```bash\n{ex}\n```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))
    else:
        message = await ctx.channel.send(f"```src.cogs.{cog} loaded!```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))

@bot.command()
async def cog_unload(ctx: commands.Context, cog: str):
    """_summary_

    Args:
        ctx (commands.Context): _description_
        cog (str): _description_
    """
    if ctx.author.id not in bot.OWNERS:
        return
    try:
        bot.unload_extension(f"src.cogs.{cog}")
    except BaseException as ex:
        message = await ctx.channel.send(f"Exception:\n```bash\n{ex}\n```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))
    else:
        message = await ctx.channel.send(f"```src.cogs.{cog} unloaded!```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))


@bot.command()
async def cog_reload(ctx: commands.Context, cog: str):
    """_summary_

    Args:
        ctx (commands.Context): _description_
        cog (str): _description_
    """
    if ctx.author.id not in bot.OWNERS:
        return
    try:
        bot.unload_extension(f"src.cogs.{cog}")
        await asyncio.sleep(1)
        bot.load_extension(f"src.cogs.{cog}")
    except BaseException as ex:
        message = await ctx.channel.send(f"Exception:\n```bash\n{ex}\n```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))
    else:
        message = await ctx.channel.send(f"```src.cogs.{cog} reloaded!```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))


@bot.command()
async def remove_cog(ctx: commands.Context, cog: str):
    """_summary_

    Args:
        ctx (commands.Context): _description_
        cog (str): _description_
    """
    if ctx.author.id not in bot.OWNERS:
        return
    try:
        bot.remove_cog(name=f"{cog}")
    except BaseException as ex:
        message = await ctx.channel.send(f"Exception:\n```bash\n{ex}\n```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))
    else:
        message = await ctx.channel.send(f"```src.cogs.{cog} removed!```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))


@bot.command(name="eval")
async def eval_string(ctx, *, content):
    """_summary_

    Args:
        ctx (_type_): _description_
        content (_type_): _description_
    """
    if ctx.author.id not in bot.EVAL_OWNER:
        return
    standart_args = {
        "nextcord": nextcord,
        "commands": commands,
        "bot": bot,
        "ctx": ctx,
        "asyncio": asyncio,
        "DataBase": DataBase,
    }
    if "```" in content:
        content = "\n".join(content.split('\n')[1:-1])
    try:
        await aeval.aeval(content, standart_args, {})
    except Exception as ex:
        result = "".join(format_exception(ex, ex, ex.__traceback__))
        message = await ctx.channel.send(f"Exception:\n```bash\n{result.replace('```', '`')}\n```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))


if __name__ == "__main__":
    bot.run(configuration.discord_token)
