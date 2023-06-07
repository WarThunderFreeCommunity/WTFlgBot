import asyncio
from traceback import format_exception

import aeval

import nextcord
from extensions import nextcord


cogs_add_on_ready: list[str] = ["VoiceCog"]
cogs_add_on_start: list[str] = []


class DeleteMessage(nextcord.ui.View):
    def __init__(self, *, message, ctx):
        super().__init__(timeout=180)
        self.message = message
        self.ctx = ctx
    
    @nextcord.ui.button(label="delete this message", style=nextcord.ButtonStyle.grey)
    async def delete_message(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.ctx.author.id  == interaction.user.id:
            await interaction.message.delete()
    
    @nextcord.ui.button(label="delete all messages", style=nextcord.ButtonStyle.grey)
    async def delete_all(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.ctx.author.id == interaction.user.id:
            await self.ctx.message.delete()
            await interaction.message.delete()  

    async def on_timeout(self):
        self.delete_message.disabled = True
        self.delete_all.disabled = True
        try:
            await self.message.edit(view=self)     
        except BaseException:
            pass


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='>',
            help_command=None,
            intents=nextcord.Intents.all(),
        )
        self.DATA: dict = {
            'bot-started': False,
        }
        self.OWNERS: list[int] = []
        self.EVAL_OWNER: list[int] = []
        self.config: object = configuration

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})\n------")
        if not self.DATA['bot-started']:
            if cogs_add_on_ready:
                [bot.load_extension(f"cogs.{cog}") for cog in cogs_add_on_ready]
            application_info = await self.application_info()
            self.OWNERS.append(application_info.owner.id)
            self.EVAL_OWNER.append(application_info.owner.id)
            self.DATA['bot-started'] = True


bot = Bot()





@bot.command()
async def cog_load(ctx: commands.Context, cog: str):
    if ctx.author.id not in bot.OWNERS:
        return
    try:
        bot.load_extension(f"cogs.{cog}")
    except BaseException as ex:
        message = await ctx.channel.send(f"Exception:\n```bash\n{ex}\n```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))
    else:
        message = await ctx.channel.send(f"```cog.{cog} loaded!```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))


@bot.command()
async def cog_unload(ctx: commands.Context, cog: str):
    if ctx.author.id not in bot.OWNERS:
        return
    try:
        bot.unload_extension(f"cogs.{cog}")
    except BaseException as ex:
        message = await ctx.channel.send(f"Exception:\n```bash\n{ex}\n```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))
    else:
        message = await ctx.channel.send(f"```cog.{cog} unloaded!```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))


@bot.command()
async def cog_reload(ctx: commands.Context, cog: str):
    if ctx.author.id not in bot.OWNERS:
        return
    try:
        bot.unload_extension(f"cogs.{cog}")
        await asyncio.sleep(1)
        bot.load_extension(f"cogs.{cog}")
    except BaseException as ex:
        message = await ctx.channel.send(f"Exception:\n```bash\n{ex}\n```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))
    else:
        message = await ctx.channel.send(f"```cog.{cog} reloaded!```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))


@bot.command()
async def remove_cog(ctx: commands.Context, cog: str):
    if ctx.author.id not in bot.OWNERS:
        return
    try:
        bot.remove_cog(name=f"{cog}")
    except BaseException as ex:
        message = await ctx.channel.send(f"Exception:\n```bash\n{ex}\n```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))
    else:
        message = await ctx.channel.send(f"```cog.{cog} removed!```")
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))


@bot.command(name="eval")
async def eval_string(ctx, *, content):
    if ctx.author.id not in bot.EVAL_OWNER:
        return
    standart_args = {
        "nextcord": nextcord,
        "commands": commands,
        "bot": bot,
        "ctx": ctx,
        "asyncio": asyncio,
    }
    if "```" in content:
        content = "\n".join(content.split('\n')[1:-1])
    try:
        message = await aeval.aeval(content, standart_args, {})
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))
    except Exception as ex:
        result = "".join(format_exception(ex, ex, ex.__traceback__))
        message = await ctx.channel.send(f"Exception:\n```bash\n{result.replace('```', '`')}\n```")   
        await message.edit(view=DeleteMessage(ctx=ctx, message=message))


if __name__ == "__main__":
    """Maybe there will be tests here sometime...
    ... however, is it necessary?
    """
