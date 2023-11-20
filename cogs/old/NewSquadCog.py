import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context


class PersistentView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, prevent_update=False)
    
    @nextcord.ui.button(
        label="new thread", style=nextcord.ButtonStyle.green
    )
    async def new_thread(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is green.", ephemeral=True)




class NewSquadCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.on_init.start()

    @tasks.loop(count=1)
    async def on_init(self):
        await self.bot.sync_all_application_commands()
    
    def cog_unload(self):
        ...
    
    @nextcord.slash_command(guild_ids=[407187066582204427])
    async def squad(self, interaction: nextcord.Interaction, squad_name: str):
        thread = await interaction.channel.create_thread(
            name=squad_name,
            type=nextcord.ChannelType.public_thread,
        )
        thread.send(
            f"```Данный Thread посвящён полку `{squad_name}`!\n"
            f"Для добавления своего полка напишите: @hop92```"
        )
        await interaction.send("ok", ephemeral=True)


    @commands.command()
    async def squadmsg(self, ctx: Context):
        return
        if ctx.author.id not in self.bot.OWNERS:
            return
        await ctx.send("squadtemp", view=PersistentView())


# on_ready cog!
def setup(bot: Bot):
    print("NewSquadCog loaded!")
    bot.add_cog(NewSquadCog(bot))
