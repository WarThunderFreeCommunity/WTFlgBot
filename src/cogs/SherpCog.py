from typing import Optional
import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context
from nextcord.utils import MISSING


class SherpDeleteView(nextcord.ui.View):
    def __init__(self, lang="ru"):
        super().__init__(timeout=None, prevent_update=False)
        self.data = {

        } if lang == "ru" else {

        }

    @nextcord.ui.button(
    label="delete thread", style=nextcord.ButtonStyle.green, custom_id="SherpCog:SherpDeleteView:delete_channel"
    )
    async def delete_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.channel.delete()


class SherpMainView(nextcord.ui.View):
    def __init__(self, lang="ru"):
        super().__init__(timeout=None, prevent_update=False)
        self.lang = lang
        self.data = {
            "become_sharp_label": "Подать заявку на становление шерпом",
            "find_sherp_label": "Подать заявку на поиск шерпа",
        } if lang == "ru" else {
            
        }
        self.become_sherp.label = self.data["become_sharp_label"]
        self.find_sherp.label = self.data["find_sherp_label"]


    @nextcord.ui.button(
        label=None, style=nextcord.ButtonStyle.green, custom_id="SherpCog:SherpMainView:become_sharp"
    )
    async def become_sherp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True, ephemeral=True)
        recipient = await interaction.guild.fetch_member(1120793294931234958) #лс

        # Создаем тред и получаем его объект
        thread = await interaction.channel.create_thread(
            name=f"{interaction.user.name} new become_sherp",
            auto_archive_duration=1440
        )

        await thread.send(
            "Пожалуйста заполните заявку такую то такую то\n"
            f"Укажите \n* это\n* и это\n*и это ещё\n{recipient.mention}",
            view=SherpDeleteView()
        )
        
        # Устанавливаем права доступа для треда
        #await thread.add_user() # любой админ
        await thread.add_user(interaction.user)
        
        # Отправляем jump_url в личное сообщение получателю
        await recipient.send(
            f"A new thread '{interaction.user.name} new become_sherp' "
            f"has been created!\n[Click here to jump]({thread.jump_url})"
        )
        await interaction.send(
            f"New thread 'become_sherp' created!\n[Click here to jump]({thread.jump_url})",
            ephemeral=True
        )

    @nextcord.ui.button(
        label=None, style=nextcord.ButtonStyle.green, custom_id="SherpCog:SherpMainView:find_sherp"
    )
    async def find_sherp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True, ephemeral=True)
        role: nextcord.Role = interaction.guild.get_role(1136308585551384677)
        channel = await interaction.guild.fetch_channel(1136309824334856232) # шерп приватный

        thread = await channel.create_thread(
            name=f"{interaction.user.name} new find_sherp",
            auto_archive_duration=1440
        )
        await thread.send(
            "Пожалуйста заполните заявку такую то такую то\n"
            f"Укажите \n* это\n* и это\n*и это ещё\n",
            view=SherpDeleteView()
        )
        await thread.add_user(interaction.user)
        for member in role.members:
            await thread.add_user(member)

        message: nextcord.Message = await channel.send(f"Новая заявка на тред! {thread.jump_url}")
        await interaction.send(
            f"New thread 'become_sherp' created!\n[Click here to jump]({thread.jump_url})",
            ephemeral=True
        )




class SherpCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.on_init.start()

    @tasks.loop(count=1)
    async def on_init(self):
        ...
    
    def cog_unload(self):
        self.bot.remove_view(view=SherpDeleteView())
        self.bot.remove_view(view=SherpMainView())

    @commands.command()
    async def sherpmsg(self, ctx: Context, lang="ru"):
        await ctx.send("test", view=SherpMainView())


# on_ready cog!
def setup(bot: Bot):
    print("SherpCog loaded!")
    bot.add_view(SherpDeleteView())
    bot.add_view(SherpMainView())
    bot.add_cog(SherpCog(bot))
