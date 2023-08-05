import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context


class PersistentView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, prevent_update=False)

    @nextcord.ui.button(
        label="Green", style=nextcord.ButtonStyle.green, custom_id="persistent_view:green"
    )
    async def green(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is green.", ephemeral=True)

    @nextcord.ui.button(
        label="Red", style=nextcord.ButtonStyle.red, custom_id="persistent_view:red"
    )
    async def red(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is red.", ephemeral=True)

    @nextcord.ui.button(
        label="Grey", style=nextcord.ButtonStyle.grey, custom_id="persistent_view:grey"
    )
    async def grey(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is grey.", ephemeral=True)


class ExampleCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.on_init.start()

    @tasks.loop(count=1)
    async def on_init(self):
        await self.bot.sync_all_application_commands()

    def cog_unload(self):
        print(self.bot.persistent_views)
        self.bot.remove_view(view=PersistentView())
        print(self.bot.persistent_views)

    @commands.command()
    async def create(self, ctx: Context):
        await ctx.send("test", view=PersistentView())

    @nextcord.slash_command(guild_ids=[1049328588249374741])
    async def prepare(self, interaction: nextcord.Interaction):
        await interaction.send("test", view=PersistentView())


# on_ready cog!
def setup(bot: Bot):
    print("ExampleCog loaded!")
    bot.add_view(PersistentView())
    bot.add_cog(ExampleCog(bot))
