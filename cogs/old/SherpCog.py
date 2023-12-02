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
        label="закрыть заявку", style=nextcord.ButtonStyle.green, custom_id="SherpCog:SherpDeleteView:close_channel"
    )
    async def close_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id not in [239772523779063808, 451008564018806784] \
        and not interaction.user.guild_permissions.administrator:
            return
        await interaction.send(f"Заявка закрыта: {interaction.user.name}")
        await interaction.channel.edit(locked=True)


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
        recipients = [
            #(await interaction.guild.fetch_member(1120793294931234958)), # hop92
            (await interaction.guild.fetch_member(239772523779063808)), # механик
            (await interaction.guild.fetch_member(451008564018806784)), # WTEXP глава
        ]

        # Создаем тред и получаем его объект
        thread = await interaction.channel.create_thread(
            name=f"{interaction.user.name} new become_sherp",
            auto_archive_duration=1440
        )

        await thread.send(
            "<@&1136308585551384677>\n"
            "Пожалуйста дождитесь ответа от модерации;\n"
            f"Пока можете рассказать о себе и вашем опыте в игре WT",
            view=SherpDeleteView()
        )

        await thread.add_user(interaction.user)
        for admin in recipients:
            await thread.add_user(admin)
            await admin.send(
                f"Новая заявка на шерпа: '{interaction.user.name} new become_sherp'\n"
                f"[Click here to jump]({thread.jump_url})"
            )
        await interaction.send(
            f"Ваше заявление тут: [Click here to jump]({thread.jump_url})",
            ephemeral=True
        )

    @nextcord.ui.button(
        label=None, style=nextcord.ButtonStyle.green, custom_id="SherpCog:SherpMainView:find_sherp"
    )
    async def find_sherp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True, ephemeral=True)
        role: nextcord.Role = interaction.guild.get_role(1136308585551384677)
        channel_sherp = await interaction.guild.fetch_channel(1136309824334856232) # шерп приватный

        thread = await interaction.channel.create_thread(
            name=f"{interaction.user.name} человеку нужен шерп!",
            auto_archive_duration=1440
        )
        await thread.send(
            content=f"{interaction.user.mention}\n"
                "Пожалуйста, заполните заявку:\n"
                "1. Тип техники (Авиация, наземка, флот);\n"
                "2. Суть вопроса для дальнейшего диалога;\n"
                "3. Укажите ваш Боевой рейтинг техники, по которой возникли вопросы.",
            view=SherpDeleteView()
        )

        await thread.add_user(interaction.user)
        for member in role.members:
            await thread.add_user(member)

        await channel_sherp.send(f"<@&1136308585551384677>, новая заявка на шерпа: {thread.jump_url}")

        await interaction.send(
            f"Ваша заявку тут: [Click here to jump]({thread.jump_url})",
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
        embed = nextcord.Embed(
            description=f"## Требования к шерпам:\n"
                "1. Неплохая статистика (K\D от 1.4 в ТРБ и 1.2 в АРБ);\n"
                "2. От 10к боёв;\n"
                "3. От 16 лет с хорошим микрофоном;\n" 
                "4. Готовые помогать другим по игровым вопросам БЕЗВОЗМЕЗДНО;\n"
                "5. Стрессоустойчивость.\n"
                "6. Умение чётко выражать свои мысли;\n"
                "7. Иметь навыки учителя.\n"
        )
        await ctx.send(embed=embed, view=SherpMainView())


# on_ready cog!
def setup(bot: Bot):
    print("SherpCog loaded!")
    bot.add_view(SherpDeleteView())
    bot.add_view(SherpMainView())
    bot.add_cog(SherpCog(bot))
