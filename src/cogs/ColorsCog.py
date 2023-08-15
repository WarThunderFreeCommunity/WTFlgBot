from copy import deepcopy
import nextcord
from nextcord.ext import tasks, commands
from nextcord.ext.commands import Bot, Cog, Context


guild_ids = [407187066582204427]
ru_role_id: int = 1133732418126348380
en_role_id: int = 1133732458962104390

marhsal_role_id: int = 1135852336783298560
general_role_id: int = 1135852114371936276

admin_rights_id: int = 497644678506741760

test_role: int = 993964119512318122


main_message_text = \
"""
```
В данном сообщении вы можете выбрать цвет своего никнейма на нашем сервере. \n
In this message you can choose the color of your nickname on our server.
```
"""
main_embed = nextcord.Embed.from_dict({
    "title": "Welcome to the War Thunder LFG",
    "description": main_message_text,
    "color": 0xE74C3C,
})


class Dropdown(nextcord.ui.Select):
    def __init__(self, lang):
        self.emojies = {
            "red": "🟥:1140639366776094780",
            "yellow": "🟨:1140639666794676274",
            "orange": "🟧:1140639837377007657",
            "green": "🟩:1140639556467708024",
            "turquoise": "🟩:1140640375002910771",
            "light blue": "🟦:1140640850087522384",
            "dark blue": "🟦:1140639503690768504",
            "purple": "🟪:1140639562268430437",
            "pink": "💄:1140639779831173220",
            "brown": "🐻:1140639890690809966",
            "silver": "🐺:1140639968818122772",
            "grey": "🦍:1140640103799210125",
            "black": "⬛:1140640149403869305",
            "white": "⬜:1141001770772988034",


        }
        self.data = {
            "red": "Красный",
            "yellow": "Жёлтый",
            "orange": "Оранжевый",
            "green": "Зелёный",
            "turquoise": "Бирюзовый",
            "light blue": "Светло-синий",
            "dark blue": "Тёмно-синий",
            "purple": "Фиолетовый",
            "pink": "Розовый",
            "brown": "Коричневый",
            "silver": "Стальной",
            "grey": "Серый",
            "black": "Чёрный",
            "white": "Белый",
            "color": "Твой любимый цвет это...",
            "placeholder": "Выберите свой любимый цвет...",
            "interaction_removed": "Успешно удалён цвет",
            "interaction_added": "Успешно добавлен цвет",
        } if lang == "RU" else {
            "red": "Red",
            "yellow": "Yellow",
            "orange": "Orange",
            "green": "Green",
            "turquoise": "Turqouise",
            "light blue": "Light blue",
            "dark blue": "Dark blue",
            "purple": "Purple",
            "pink": "Pink",
            "brown": "Brown",
            "silver": "Silver",
            "grey": "Grey",
            "black": "Black",
            "white": "White",
            "color": "Your favourite colour is ...",
            "placeholder": "Choose your favourite colour...",
            "interaction_removed": "Succesfully deleted colour",
            "interaction_added": "Succesfully added colour",
        }
        options = [
            nextcord.SelectOption(
                label=self.data[emoji],
                description=self.data["color"],
                emoji=self.emojies[emoji].split(":")[0],
                value=emoji,
            )
            for emoji in self.emojies
        ]

        super().__init__(
            placeholder=self.data["placeholder"],
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: nextcord.Interaction):
        try:
            user_roles_id = [role.id for role in interaction.user.roles]
            allowed_roles_id = [marhsal_role_id, general_role_id, admin_rights_id]
            if not any(role_id in user_roles_id for role_id in allowed_roles_id):
                await interaction.send(self.data["error_msg"], ephemeral=True)
                return
            await interaction.response.defer(with_message=True, ephemeral=True)
            selected_role_id = int(self.emojies[self.values[0]].split(":")[1]) # Id выбранной роли
            interaction_roles_list = [] # Все id роли участника
            all_colours_list = [] # Все id цветов
            for interaction_roles in interaction.user.roles:
                interaction_roles_list.append(interaction_roles.id)

            for all_colours in self.emojies.values():
                all_colours = all_colours.split(":")[1]
                all_colours_list.append(int(all_colours))

            if selected_role_id in interaction_roles_list:
                role = nextcord.utils.get(interaction.guild.roles, id=selected_role_id)
                await interaction.user.remove_roles(role)
                await interaction.send(
                    f"{self.data['interaction_removed']}: {self.data[self.values[0]]}", ephemeral=True
                )
            else:
                for role_member in interaction_roles_list:
                    if role_member in all_colours_list:
                        role = nextcord.utils.get(interaction.guild.roles, id=role_member)
                        await interaction.user.remove_roles(role)
                member, guild = interaction.user, interaction.guild
                role_set = guild.get_role(selected_role_id)
                await member.add_roles(role_set)
                await interaction.send(f"{self.data['interaction_added']}: {self.data[self.values[0]]}", ephemeral=True)
        except nextcord.errors.NotFound as ex:
            await interaction.send("```error: Unknown interaction```")
        except BaseException as ex:
            print(ex)


class MainButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, prevent_update=False)

    @nextcord.ui.button(
        label="ВЫБРАТЬ ЦВЕТ НИКНЕЙМА",
        style=nextcord.ButtonStyle.green,
        custom_id="MainButtons:color_ru",
    )
    async def color_ru(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        view = nextcord.ui.View()
        view.add_item(Dropdown("RU"))
        await interaction.send("Выберите нужный цвет..", view=view, ephemeral=True)

    @nextcord.ui.button(
        label="CHOOSE NICKNAME COLOR",
        style=nextcord.ButtonStyle.green,
        custom_id="MainButtons:color_en",
    )
    async def color_en(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        embed = ...
        view = nextcord.ui.View()
        view.add_item(Dropdown("EN"))
        await interaction.send("Select the desired color..", view=view, ephemeral=True)
                               

class CogColors(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.obj_guild = self.bot.get_guild(974022203987357766)
        self.on_init.start()
        self.bot.add_view(MainButtons())

    def __del__(self):
        ...

    @tasks.loop(count=1, reconnect=False)
    async def on_init(self):
        pass
 
    def cog_unload(self):
        self.bot.remove_view(MainButtons())

    @commands.command()
    async def ColorsMsg(self, ctx: Context):
        if ctx.author.id not in self.bot.OWNERS:
            return
        await ctx.message.delete()
        await ctx.channel.send(
            embed=deepcopy(main_embed),
            view=MainButtons()
        )


def setup(bot: Bot) -> None:
    print(f"{__name__.split('.')[2]} loaded!")
    bot.add_view(MainButtons())
    bot.add_cog(CogColors(bot))
