import os
from typing import Final

import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context

CURRENT_DIR: Final = os.path.dirname(os.path.abspath(__file__))
PARRENT_DIR: Final = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))

DATA_DIR: Final = os.path.join(PARRENT_DIR, 'data')
DATA_MESSAGES_DIR: Final = os.path.join(DATA_DIR, 'messages')


class StafModal(nextcord.ui.Modal):
    def __init__(self, modal_name):
        self.modal_name = modal_name
        super().__init__(
            title=f"Заявка на {modal_name}",
            timeout=5 * 60,
        )
        self.text_inputs: dict = {
            "Moderator": {
                "name": [
                    "ваше имя и возраст",
                    "Илья, 19 лет"
                ],
                "time_zone": [
                    "ваш часовой полос и прайм-тайм",
                    "+6 МСК, 12:00 - 20:00",
                ],
                "experience": [
                    "имеется ли у вас опыт в данной сфере деятельности?",
                    "Если да - расскажите",
                ],
                "skills": [
                    "какие иностранные языки вы знаете?",
                    "Русский родной, английский разговорный.."
                ],
                "autobiography": [
                    "расскажите немного о себе",
                    "Большую часть онлайн с ПК, продолжение вашего рассказа.."
                ],
            },
            "Eventer": {
                "name": [
                    "ваше имя и возраст",
                    "Ева, 19 лет"
                ],
                "time_zone": [
                    "ваш часовой полос и прайм-тайм",
                    "+3 МСК, 08:00 - 16:00",
                ],
                "experience": [
                    "есть ли у вас опыт проведения мероприятий, организация?",
                    "Если да то укажите какой",
                ],
                "skills": [
                    "какими навыками общения вы обладаете",
                    "Вежливость, серьзность...",
                ],
                "autobiography": [
                    "расскажите немного о себе",
                    "Ваш рассказ"
                ],
            },
            "SystemAdmin": {
                "name": [
                    "ваше имя и возраст",
                    "Мария, 16 лет"
                ],
                "time_zone": [
                    "ваш часовой полос и прайм-тайм",
                    "-3 МСК, 10:00 - 18:00",
                ],
                "experience": [
                    "имеется ли у вас опыт на данной должности",
                    "Если да, то приложите пример проекта",
                ],
                "skills": [
                    "какие ключевые навыки вы   имеете",
                    "python, discord.py, SQL, bash..."
                ],
                "autobiography": [
                    "расскажите немного о себе",
                    "Ваш рассказ"
                ],
            },
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
            max_length=300,
        )
        self.time_zone = create_input(
            *self.text_inputs[modal_name]["time_zone"],
            max_length=300,
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
        colors = {
            "Moderator" : 0x0079B1,
            "Eventer": 0xF2FD00,
            "SystemAdmin": 0xD22D2D
        }
        embed = nextcord.Embed(
            title=f"{interaction.user.mention}({interaction.user.id}) создал новую заявку на {self.modal_name}!",
            color=colors[self.modal_name]
        )
        for item in self.items:
            embed.add_field(
                name=self.text_inputs[self.modal_name][item[1]][0],
                value=item[0].value
            )
        channel = interaction.guild.get_channel(1121101138423451659)
        if channel:
            await channel.send(embed=embed)
        await interaction.response.send_message(
            content="Заявка отправлена!", ephemeral=True
        )


class StafSelect(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="Moderator"),
            nextcord.SelectOption(label="Eventer"),
            nextcord.SelectOption(label="SystemAdmin"),
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

    def __del__(self):
        pass

    def cog_unload(self):
       self.bot.remove_view(StafSelectView())

    @commands.command()
    async def ticket_staff_messages(self, ctx: Context):
        if ctx.author.id not in self.bot.OWNERS:
            return
        await ctx.message.delete()
        embed = nextcord.Embed(
            title="Привет! Тут вы можете подать заявку на сотрудника сервера.",
            color=0xFF0000
        )
        view = StafSelectView()
        await ctx.channel.send(embed=embed, view=view)


def setup(bot: Bot) -> None:
    print("RecruitTempCog.py loaded")
    bot.add_cog(StafPosition(bot))