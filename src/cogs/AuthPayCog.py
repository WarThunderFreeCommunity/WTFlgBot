import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context

from extensions.DBWorkerExtension import DataBase


cog_name = "AuthPayCog"


class AuthButtonsView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, prevent_update=False)

    @nextcord.ui.button(
        label="test", style=nextcord.ButtonStyle.green, custom_id=f"{cog_name}:PersistentView:test"
    )
    async def test(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is test.", ephemeral=True)


class AuthPay(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.on_init.start()

    @tasks.loop(count=1, reconnect=False)
    async def on_init(self):
        await self.bot.sync_all_application_commands()

    def cog_unload(self):
        self.bot.remove_view(view=AuthButtonsView())

    @commands.command()
    async def auth(self, ctx: Context):
        await ctx.send("test", view=AuthButtonsView())


def setup(bot: Bot):
    print(f"{cog_name} loaded!")
    bot.add_view(AuthButtonsView())
    bot.add_cog(AuthPay(bot))

