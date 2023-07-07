import os
import base64
import random
import string
import asyncio
import datetime
from copy import deepcopy
from urllib.parse import urlencode

import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context
from glQiwiApi import QiwiWrapper

import configuration as cnfg

ru_role_id: int = 795232311477272576
en_role_id: int = 795232315579564032
main_message_text = """
```
Вы присоединились к Fan серверу War Thunder\n
You have joined the War Thunder Fan Server
```
```
Выберите свой язык нажав на кнопку:  Russian / Englich\n
Select your language by clicking on the button: Russian / Englich
```
```
Вы также можете купить рекламу или дополнительные возможности, используя канал #Выбор-ролей\n
You can also order advertising or additional features using the channel #Select-Roles
```
"""

main_embed = nextcord.Embed.from_dict(
    {
        "title": "Welcome to the War Thunder Сommunity Server",
        "description": main_message_text,
        "color": 0xE74C3C,
    }
)


class MainAuthButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, prevent_update=False)
        self.add_item(
            nextcord.ui.Button(
                label="#Выбор-ролей",
                url="https://discord.com/channels/691182902633037834/1126098284952436806/",
            )
        )
        self.add_item(
            nextcord.ui.Button(
                label="#Select-Roles",
                url="https://discord.com/channels/691182902633037834/1126098284952436806/",
            )
        )

    @nextcord.ui.button(
        label="RUSSIAN",
        style=nextcord.ButtonStyle.green,
        custom_id="AuthCog:MainAuthButtons:RUSSIAN",
    )
    async def russian(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        await interaction.response.defer(ephemeral=True, with_message=True)
        member, guild = interaction.user, interaction.guild
        role = guild.get_role(ru_role_id)
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.send("Удалена RUSSIAN роль", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.send("Добавлена RUSSIAN роль", ephemeral=True)

    @nextcord.ui.button(
        label="ENGLISH",
        style=nextcord.ButtonStyle.green,
        custom_id="AuthCog:MainAuthButtons:ENGLISH",
    )
    async def english(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        await interaction.response.defer(ephemeral=True, with_message=True)
        member, guild = interaction.user, interaction.guild
        role = guild.get_role(en_role_id)
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.send("Removed ENGLISH role", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.send("Added ENGLISH role", ephemeral=True)


class Dropdown(nextcord.ui.Select):
    def __init__(self, lang):
        self.emojies = {
            "white": "⬜:937593712391901184",
            "yellow": "🟨:937593431591641100",
            "green": "🟩:937593680750080030",
            "purple": "🟪: 937593682620719164",
            "black": "⬛:939886116113350706",
            "orange": "🟧:939889190924075018",
            "blue": "🟦:939888364994330674",
            "brown": "🟫:939895587422208020"
        }
        self.data = {
            "white": "Белый",
            "yellow": "Желтый",
            "green": "Зелёный",
            "purple": "Фиолетовый",
            "black": "Чёрный",
            "orange": "Оранжевый",
            "blue": "Синий",
            "brown": "Коричневый",
            "color": "Твой любимый цвет это..."
        } if lang == "RU" else {
            "white": "White",
            "yellow": "Yellow",
            "green": "Green",
            "purple": "Purple",
            "black": "Black",
            "orange": "Orange",
            "blue": "Blue",
            "brown": "Brown",
            "color": "Your favourite colour is ..."
        }
        options = [
            nextcord.SelectOption(
                label=self.data[emoji],
                description=self.data["color"],
                emoji=self.emojies[emoji].split(':')[0]
            ) for emoji in self.emojies
        ]

        super().__init__(
            placeholder="Choose your favourite colour...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: nextcord.Interaction):
        # TODO выдача ролей
        await interaction.response.send_message(
            f"Your favourite colour is {self.values[0]}",
            ephemeral=True
        )


class ColourButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, prevent_update=False)

    @nextcord.ui.button(
        label="ВЫБРАТЬ ЦВЕТ НИКНЕЙМА",
        style=nextcord.ButtonStyle.green,
        custom_id="AuthCog:ColourButtons:color_ru",
    )
    async def color_ru(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        print(1)
        embed = ...
        view = nextcord.ui.View()
        view.add_item(Dropdown("RU"))
        await interaction.send("Цвет...", view=view, ephemeral=True)

    @nextcord.ui.button(
        label="CHOOSE NICKNAME COLOR",
        style=nextcord.ButtonStyle.green,
        custom_id="AuthCog:ColourButtons:color_en",
    )
    async def color_en(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        embed = ...
        view = nextcord.ui.View()
        view.add_item(Dropdown("EN"))
        await interaction.send("Color...", view=view, ephemeral=True)


class AuthCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.obj_guild = self.bot.get_guild(691182902633037834)
        self.on_init.start()
        self.bot.add_view(MainAuthButtons())
        self.bot.add_view(ColourButtons())

    def __del__(self):
        ...

    @tasks.loop(count=1, reconnect=False)
    async def on_init(self):
        pass

    def cog_unload(self):
        self.bot.remove_view(ColourButtons())
        self.bot.remove_view(MainAuthButtons())

    @commands.command()
    async def authmsg(self, ctx: Context):
        if ctx.author.id not in self.bot.OWNERS:
            return
        await ctx.message.delete()
        await ctx.channel.send(embed=deepcopy(main_embed), view=MainAuthButtons())
    
    @commands.command()
    async def rolesmsg(self, ctx: Context):
        if ctx.author.id not in self.bot.OWNERS:
            return
        await ctx.message.delete()
        await ctx.channel.send("Выбери свой цвет\nSelect your color", view=ColourButtons())



def setup(bot: Bot) -> None:
    print("AuthCog.py loaded")
    bot.add_view(MainAuthButtons())
    bot.add_cog(AuthCog(bot))
