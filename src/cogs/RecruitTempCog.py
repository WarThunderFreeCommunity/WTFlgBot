from traceback import format_exception

import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context


GUILDS_RECRUIT_CHANNELS = {
    691182902633037834: 1121101138423451659,
    1027302631691014215: 1122859941686951997
}


class DenyStafButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, prevent_update=False)
    
    @nextcord.ui.button(label="Отправить уведомление человеку", style=nextcord.ButtonStyle.grey, custom_id="RecruitTempCog:DenyStafButtons:allow_user")
    async def allow_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        modal = nextcord.ui.Modal(
            title="DM Уведомление о принятии",
            timeout=5*60
        )
        modal.add_item(member_id := nextcord.ui.TextInput(
            label="Введите id человека для уведомления",
            placeholder="0123456789",
            required=True,
        ))
        modal.add_item(reason := nextcord.ui.TextInput(
            label="Укажите комментарий пользователю (по желанию)",
            placeholder="Добро пожаловать в коллектив!",
            required=False,
        ))
        modal.completed = False
        modal.ex = False
        async def modal_callback(interaction: nextcord.Interaction):
            try:
                member = nextcord.utils.get(
                    interaction.guild.members, id=int(member_id.value)
                )
                await member.send(f"Уважаемый {member.mention}, мы рассмотрели вашу заявку, с уважением, команда WTCommunityDiscord\n"
                                  f"В скором времени с вами может связаться администрация проекта.\n"
                                  f"Модератор: {interaction.user.mention}\n{f'Комментарий: {reason.value}' if reason.value else ''}")
                await interaction.send("Комментарий отправлен!", ephemeral=True)
                modal.completed = True
            except BaseException as ex:
                modal.completed = False
                modal.ex = True
                await interaction.send("Что-то пошло не так! Возможно заблокирвоаны DM.", ephemeral=True)
                raise ex
            finally:
                modal.stop()
        modal.callback = modal_callback
        await interaction.response.send_modal(modal)
        if (await modal.wait()):
            if not modal.ex:
                await interaction.send("Вы не отправили ответ!", ephemeral=True)
            return
        if modal.completed:
            embed = nextcord.Embed(
                description=f"{interaction.user.mention}({interaction.user.id}) отправил уведомление на данную заявку!"
            )
            button.disabled = True
            self.deny_user.disabled = True
            self.close_request = True
        else:
            embed = nextcord.Embed(
                description=f"{interaction.user.mention}({interaction.user.id}) попытался отправить уведомление на данную заявку! Возможно DM заблокированы.\nВы можете попытаться отправить ещё раз..."
            )
        if reason.value:
            embed.add_field(
                name="уведомление: ".upper(),
                value=f"```{reason.value}```",
                inline=False
            )
        embeds = interaction.message.embeds
        embeds.append(embed)
        if len(embeds) > 4:
            button.disabled = True
            self.deny_user.disabled = True
            self.close_request = True
        await interaction.message.edit(embeds=embeds, view=self)

    @nextcord.ui.button(label="Отказать человеку", style=nextcord.ButtonStyle.red, custom_id="RecruitTempCog:DenyStafButtons:deny_user")
    async def deny_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        modal = nextcord.ui.Modal(
            title="DM Уведомление от отказе",
            timeout=5*60
        )
        modal.add_item(member_id := nextcord.ui.TextInput(
            label="Введите id человека для уведомления",
            placeholder="0123456789",
            required=True,
        ))
        modal.add_item(reason := nextcord.ui.TextInput(
            label="Укажите причину (по желанию)",
            placeholder="Не нравитесь модераторам",
            required=False,
        ))
        modal.completed = False
        modal.ex = False
        async def modal_callback(interaction: nextcord.Interaction):
            try:
                member = nextcord.utils.get(
                    interaction.guild.members, id=int(member_id.value)
                )
                await member.send(f"Уважаемый {member.mention}, в вашей заявкей отказано, с уважением,F команда WTCommunityDiscord\n"
                                  f"Модератор: {interaction.user.mention}\n{f'Причина: {reason.value}' if reason.value else ''}")
                await interaction.send("Отказ отправлен!", ephemeral=True)
                modal.completed = True
            except BaseException as ex:
                modal.completed = False
                modal.ex = True
                await interaction.send("Что-то пошло не так! Возможно заблокирвоаны DM.", ephemeral=True)
                raise ex
            finally:
                modal.stop()
        modal.callback = modal_callback
        await interaction.response.send_modal(modal) 
        if (await modal.wait()):
            if not modal.ex:
                await interaction.send("Вы не отправили ответ!", ephemeral=True)
            return
        if modal.completed:
            embed = nextcord.Embed(
                description=f"{interaction.user.mention}({interaction.user.id}) отправил отказ на данную заявку!"
            )
            button.disabled = True
            self.allow_user.disabled = True
            self.close_request = True
        else:
            embed = nextcord.Embed(
                description=f"{interaction.user.mention}({interaction.user.id}) попытался отправить отказ на данную заявку! Возможно DM заблокированы.\nВы можете попытаться отправить ещё раз..."
            )
        if reason.value:
            embed.add_field(
                name="комментарий: ".upper(),
                value=f"```{reason.value}```",
                inline=False
            )
        embeds = interaction.message.embeds
        embeds.append(embed)
        if len(embeds) > 4:
            button.disabled = True
            self.allow_user.disabled = True
            self.close_request = True
        await interaction.message.edit(embeds=embeds, view=self)
    
    @nextcord.ui.button(label="Закрыть заявку", style=nextcord.ButtonStyle.red, custom_id="RecruitTempCog:DenyStafButtons:close_request")
    async def close_request(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        button.disabled = True
        self.deny_user.disabled = True
        self.allow_user.disabled = True
        embeds = interaction.message.embeds
        embeds.append(nextcord.Embed(
                description=f"{interaction.user.mention}(`{interaction.user.id}`) закрыл заявку!"
        ))
        await interaction.message.edit(embeds=embeds, view=self)
        await interaction.send("Заявка спешно закрыта!", ephemeral=True)


class StafModal(nextcord.ui.Modal):
    def __init__(self, modal_name):
        self.modal_name = modal_name
        super().__init__(
            title=f'Заявка на должность "{modal_name}"',
            timeout=60 * 60,
        )
        self.text_inputs: dict = {
            "Модератор": {
                "name": [
                    "ваше имя и возраст".upper(),
                    "Илья, 19 лет"
                ],
                "time_zone": [
                    "ваш часовой пояс и прайм-тайм".upper(),
                    "+6 МСК, 12:00 - 20:00",
                ],
                "experience": [
                    "имеется ли у вас опыт на данной должности?".upper(),
                    "Если да - расскажите",
                ],
                "skills": [
                    "какие иностранные языки вы знаете?".upper(),
                    "Русский родной, английский разговорный.."
                ],
                "autobiography": [
                    "расскажите немного о себе".upper(),
                    "Большую часть онлайн с ПК..."
                ],
            },
            "Ивент организатор": {
                "name": [
                    "ваше имя и возраст".upper(),
                    "Ева, 19 лет"
                ],
                "time_zone": [
                    "ваш часовой пояс и прайм-тайм".upper(),
                    "+3 МСК, 08:00 - 16:00",
                ],
                "experience": [
                    "есть ли у вас опыт проведения мероприятий?".upper(),
                    "Если да то укажите какой",
                ],
                "skills": [
                    "какими навыками общения вы обладаете".upper(),
                    "Вежливость, серьзность...",
                ],
                "autobiography": [
                    "расскажите немного о себе".upper(),
                    "Ваш рассказ"
                ],
            },
            "Системный администратор": {
                "name": [
                    "ваше имя и возраст".upper(),
                    "Мария, 16 лет"
                ],
                "time_zone": [
                    "ваш часовой пояс и прайм-тайм".upper(),
                    "-3 МСК, 10:00 - 18:00",
                ],
                "experience": [
                    "имеется ли у вас опыт на данной должности".upper(),
                    "Если да, то приложите пример проекта",
                ],
                "skills": [
                    "какие ключевые навыки вы имеете".upper(),
                    "python, discord.py, SQL, bash..."
                ],
                "autobiography": [
                    "расскажите немного о себе".upper(),
                    "Ваш рассказ"
                ],
            },
            "Дизайнер": {
                "name": [
                    "ваше имя и возраст".upper(),
                    "Полина, 20 лет"
                ],
                "time_zone": [
                    "ваш часовой пояс и прайм-тайм".upper(),
                    "0 МСК, 18:00 - 20:00",
                ],
                "experience": [
                    "имеется ли у вас опыт на данной должности".upper(),
                    "Если да, то приложите пример проекта",
                ],
                "skills": [
                    "какие ключевые навыки вы имеете".upper(),
                    "Adobe Photoshop, Paint Tool SAI, Adobe Illustrator..."
                ],
                "autobiography": [
                    "расскажите немного о себе".upper(),
                    "Ваш рассказ"
                ],
            }
        }

        @staticmethod
        def create_input(
            label,
            placeholder,
            required=True,
            style=nextcord.TextInputStyle.short,
            min_length=None,
            max_length=None,
        ):
            return nextcord.ui.TextInput(
                label=label,
                placeholder=placeholder,
                required=required,
                style=style,
                min_length=min_length,
                max_length=max_length,
            )

        # Define the inputs using the create_input function
        self.name = create_input(
            *self.text_inputs[modal_name]["name"],
        )
        self.time_zone = create_input(
            *self.text_inputs[modal_name]["time_zone"],
        )
        self.experience = create_input(
            *self.text_inputs[modal_name]["experience"],
            style=nextcord.TextInputStyle.paragraph,
        )
        self.skills = create_input(
            *self.text_inputs[modal_name]["skills"],
            style=nextcord.TextInputStyle.paragraph,
        )
        self.autobiography = create_input(
            *self.text_inputs[modal_name]["autobiography"],
            style=nextcord.TextInputStyle.paragraph,
        )

        # Store the inputs in a list
        self.items = [
            [self.name, "name"],
            [self.time_zone, "time_zone"],
            [self.experience, "experience"],
            [self.skills, "skills"],
            [self.autobiography, "autobiography"],
        ]

        # Add the inputs to the view
        for item in self.items:
            self.add_item(item[0])

    # Define the callback function to handle the submission of the form
    async def callback(self, interaction: nextcord.Interaction) -> None:
        try:
            colors = {
                "Модератор" : 0x0079B1,
                "Ивент организатор": 0xF2FD00,
                "Системный администратор": 0xD22D2D,
                "Дизайнер": 0xD22D2D,
            }
            embed = nextcord.Embed(
                description=f"{interaction.user.mention}/{interaction.user.name}(`{interaction.user.id}`) создал новую заявку на должность `{self.modal_name}`!",
                color=colors[self.modal_name]
            )
            for item in self.items:
                embed.add_field(
                    name=self.text_inputs[self.modal_name][item[1]][0],
                    value=f"```{item[0].value}```",
                    inline=False
                )
            guild = interaction.guild
            channel = guild.get_channel(GUILDS_RECRUIT_CHANNELS[guild.id])
            if channel:
                await channel.send(embed=embed, view=DenyStafButtons())
            await interaction.response.send_message(
                content="Заявка отправлена! Администраторы свяжутся с вами в личные сообщения", ephemeral=True
            )
        except BaseException as ex:
            result = "".join(format_exception(ex, ex, ex.__traceback__))
            await interaction.send(f"Что-то пошло не так, напишите в личные сообщения <@286914074422280194>\nException:\n```bash\n{result.replace('```', '`')}\n```", ephemeral=True)


class StafSelect(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="Модератор", description="Создать заявку на должность модератора"),
            nextcord.SelectOption(label="Ивент организатор", description="Создать заявку на должность ивент организатора"),
            nextcord.SelectOption(label="Системный администратор", description="Создать заявку на должность системного администратора"),
            nextcord.SelectOption(label="Дизайнер", description="Создать заявку на должность дизайнера"),
        ]

        super().__init__(
            custom_id="StafPosition:StafSelect",
            placeholder="Выберите интересующую вас должность...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.send_modal(
            StafModal(modal_name=self.values[0])
        )


class StafSelectView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, prevent_update=False)
        self.add_item(StafSelect())


class StafPosition(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.bot.add_view(StafSelectView())
        self.bot.add_view(DenyStafButtons())

    def __del__(self):
        pass

    def cog_unload(self):
       self.bot.remove_view(StafSelectView())
       self.bot.remove_view(DenyStafButtons())

    @commands.command()
    async def ticket_staff_messages(self, ctx: Context):
        if ctx.author.id not in self.bot.OWNERS:
            return
        await ctx.message.delete()
        embed = nextcord.Embed(
            title="Привет! Тут вы можете подать заявку на вступление в состав сотрудников сервера.",
            color=0xFF0000
        )
        view = StafSelectView()
        await ctx.channel.send(embed=embed, view=view)


def setup(bot: Bot) -> None:
    print("RecruitTempCog.py loaded")
    bot.add_cog(StafPosition(bot))