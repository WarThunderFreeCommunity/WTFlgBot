# Переписать по нормальному !
import os
import base64
import random
import string
import asyncio
import datetime
from copy import deepcopy
from urllib.parse import urlencode
import logging


import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context
from glQiwiApi import QiwiWrapper

from ..extensions.EXFormatExtension import ex_format
import configuration as cnfg

# Создать путь к папке "data" в директории выше
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
data_dir = os.path.join(parent_dir, 'data')

data_adver_path = os.path.join(data_dir, 'data_adver.txt')
data_vip_path = os.path.join(data_dir, 'data_vip.txt')
data_log_path = os.path.join(data_dir, '_data_log_payments.txt')

guild_ids = [1064192306904846377]
ru_role_id: int = 795232311477272576
en_role_id: int = 795232315579564032

vip_ru_role_id = 1007965606789783572
vip_en_role_id = 1085530065707733012
adv_ru_role_id = 1085540360173924412
adv_en_role_id = 1085543092582625409
booster_role_id = 753919549484564521
junior_moderator = 1038135072353689671

main_message_text = \
"""
```
В данном сообщении вы можете поддержать сервер своим донатом или заказать рекламу своего полка.\n
In this message, you can support the server with your donation or order an advertisement for your regiment.
```
"""

main_embed = nextcord.Embed.from_dict({
    "title": "Welcome to the War Thunder Сommunity Server",
    "description": main_message_text,
    "color": 0xE74C3C,
})

advertisement_ru_embed = nextcord.Embed.from_dict({
    "title": "Реклама",
    "description": "Выберите нужное значение",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
})

advertisement_en_embed = nextcord.Embed.from_dict({
    "title": "Advertisment",
    "description": "Select the desired value",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
})

vip_ru_embed = nextcord.Embed.from_dict({
    "title": "VIP",
    "description": "Выберите нужное значение",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
})

vip_en_embed = nextcord.Embed.from_dict({
    "title": "VIP",
    "description": "Select the desired value",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
})

payment_ru_embed = nextcord.Embed.from_dict({
    "title": "Оплата",
    "description": "Пожалуйста, укажите комментарий к платежу из данного сообщения",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
})

payment_en_embed = nextcord.Embed.from_dict({
    "title": "Payment",
    "description": "Please enter a comment on the payment from this message",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
})


class PaymentButtons(nextcord.ui.View):
    def __init__(self, payment_info: dict, lang: str, member: nextcord.Interaction.user):
        super().__init__()
        self.timeout = 7200
        self.payment_info = payment_info
        self.lang = lang
        self.data = [{
            "link_to_pay": "Оплатить",
            "check_payment": "Проверить платёж",
            "cancel_payment": "Отменить платёж"
        }, None] if lang == "ru" else [{
            "link_to_pay": "To pay",
            "check_payment": "Check the payment",
            "cancel_payment": "Cancel payment"
        }, None]
        self.add_item(nextcord.ui.Button(
            label=self.data[0]["link_to_pay"], url=self._generate_url()))
        self.check_payment.label = self.data[0]["check_payment"]
        self.cancel_payment.label = self.data[0]["cancel_payment"]

    @staticmethod
    def logger():
        try:
            logger = logging.getLogger('nextcord')
            logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
            handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
            logger.addHandler(handler)
        except BaseException as ex:
            print(ex_format(ex, "logger_payment"))

    def _generate_url(self) -> str:
        params = {
            "amountInteger": self.payment_info['real_summ'],
            "amountFraction": 0,
            "currency": 643,
            "extra['accountType']": "nickname",
            "extra['account']": "YUNIK",
            "blocked": ["sum", "account"],
        }
        encoded_params = {
            k: v.encode("utf-8") if isinstance(v, str) else v for k, v in params.items()
        }
        return "https://qiwi.com/payment/form/99999?" + urlencode(
            encoded_params, doseq=True
        )

    @staticmethod
    async def _check_payment(amount: float, comment: str):
        async with QiwiWrapper(
            api_access_token=cnfg.qiwi_token, phone_number=f"+{cnfg.qiwi_number}"
        ) as wrapper:
            for transaction in await wrapper.transactions():
                if (
                        transaction.status_text == "Success"
                        and transaction.sum.amount == amount
                        and transaction.comment == comment
                ):
                    return True, transaction.id
            return False, transaction.id

    @staticmethod
    def write_data(dis_id: int, type: str, real_summ: float, enrollment_summ: float, payment_id: str):
        """
        dis_id (str) - ID пользователя
        type (str) - тип покупки (от этого параметра зависит файл записи)
        """
        data_log_path = os.path.join(data_dir, '_data_log_payments.txt')
        with open(data_log_path, 'a') as log_file:
            log_file.write(
                f"{dis_id}:{type}:{real_summ:.2f}:{enrollment_summ:.2f}:{payment_id}\n")
        if type == "vip":
            data_path = os.path.join(data_dir, 'data_vip.txt')
        elif type == "adver":
            data_path = os.path.join(data_dir, 'data_adver.txt')
        with open(data_path, 'r') as data_file:
            lines = data_file.readlines()
        for i, line in enumerate(lines):
            parts = line.strip().split(':')
            if str(parts[0]) == str(dis_id):
                new_enrollment_summ = float(parts[1]) + enrollment_summ
                lines[i] = f"{dis_id}:{new_enrollment_summ:.2f}\n"
                break
        else:  # выполнится если не было break
            lines.append(f"{dis_id}:{enrollment_summ:.2f}\n")
        with open(data_path, 'w') as data_file:
            data_file.writelines(lines)


    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def check_payment(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.cancel_payment.disabled = True
        button.disabled = True
        await interaction.response.edit_message(
            content="Проверка платежа, пожалуйста, подождите, это может идти около минуты.\n"
                    "> **Не удаляйте данной сообщение.**" if self.lang == "ru" else 
                    "Payment verification, please wait, it may take about a minute.\n"
                    "> **Do not delete this message.**",
            view=self
        )
        try:
            check: bool = False
            for i in range(6):
                check, _transaction = await self._check_payment(
                    amount=float(self.payment_info["real_summ"]),
                    comment=str(self.payment_info["comment"])
                )
                if check:   
                    self.stop()
                    await interaction.edit_original_message(view=None)
                    comment_base64 = self.payment_info["comment"]
                    comment_bytes = base64.b64decode(
                        comment_base64)  # Декодируем строку из Base64
                    self.payment_info["comment"] = comment_bytes.decode(
                        'utf-8')  # Преобразуем байты в строку
                    user = interaction.user
                    guild = user.guild
                    if self.lang == "ru":
                        if self.payment_info["type"] == "adver":
                            await user.add_roles(guild.get_role(adv_ru_role_id))
                        else:
                            await user.add_roles(guild.get_role(vip_ru_role_id))
                    else:
                        if self.payment_info["type"] == "adver":
                            await user.add_roles(guild.get_role(adv_en_role_id))
                        else:
                            await user.add_roles(guild.get_role(vip_en_role_id))
                    self.write_data(
                        dis_id=self.payment_info["comment"].split(":")[0],
                        type=self.payment_info["type"],
                        real_summ=self.payment_info["real_summ"],
                        enrollment_summ=self.payment_info["enrollment_summ"],
                        payment_id=_transaction
                    )
                    break
                await asyncio.sleep(10)
            else:
                self.cancel_payment.disabled = False
                button.disabled = False
                await interaction.edit_original_message(view=self)
            await interaction.edit_original_message(
                content=("Успешно!" if self.lang == "ru" else "All ok!") if check else 
                ("Что-то пошло не так. Пожалуйста создайте тикет." if self.lang == "ru" else
                "Something went wrong. Please create a ticket.")
            )
        except BaseException as ex:
            from traceback import format_exception
            result = "".join(format_exception(ex, ex, ex.__traceback__))
            await interaction.send(f"Exception:\n```bash\n{result.replace('```', '`')}\n```", ephemeral=True)

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def cancel_payment(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        ...
        self.stop()
        await interaction.response.edit_message(view=None)
    ...


class AdvertisementButtons(nextcord.ui.View):
    def __init__(self, lang: str):
        super().__init__()
        self.lang = lang
        self.timeout = 300
        self.payment_info: dict = {
            'real_summ': None,
            'enrollment_summ': None,
            'comment': None,
            'type': "adver"
        }
        self.data = [{
            "one_day": "Одинь день 120 RUB",
            "one_month": "Один месяц 3000 RUB",
            "to_pay": "Перейти к оплате",
            "to_pay_embed": deepcopy(payment_ru_embed)
        }, None] if lang == "ru" else [{
            "one_day": "One day 120 RUB",
            "one_month": "One month 3000 RUB",
            "to_pay": "Move to pay",
            "to_pay_embed": deepcopy(payment_en_embed)
        }, None]
        self.to_pay.disabled, self.to_pay.label = True, self.data[0]["to_pay"]
        self.one_day.label = self.data[0]["one_day"]
        self.one_month.label = self.data[0]["one_month"]

    @staticmethod
    def update_buttons(button_dict: dict):
        for button, properties in button_dict.items():
            for property_name, value in properties.items():
                setattr(button, property_name, value)

    def disable_buttons(self, button: str):
        if button == "one_day":
            self.update_buttons({
                self.one_day: {"disabled": True, "style": nextcord.ButtonStyle.green},
                self.one_month: {"disabled": False, "style": nextcord.ButtonStyle.grey},
                self.to_pay: {"disabled": False, "style": nextcord.ButtonStyle.green},
            })
        elif button == "one_month":
            self.update_buttons({
                self.one_day: {"disabled": False, "style": nextcord.ButtonStyle.grey},
                self.one_month: {"disabled": True, "style": nextcord.ButtonStyle.green},
                self.to_pay: {"disabled": False, "style": nextcord.ButtonStyle.green},
            })

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def one_day(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.payment_info['real_summ'] = 120.0
        self.payment_info['enrollment_summ'] = 120.0
        self.disable_buttons("one_day")
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def one_month(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.payment_info['real_summ'] = 3000.0
        self.payment_info['enrollment_summ'] = 3600
        self.disable_buttons("one_month")
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def to_pay(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()
        comment = f"{interaction.user.id}:" + ''.join(random.choices(
            string.ascii_letters + string.digits + string.punctuation,
            k=10))
        comment_base64 = base64.b64encode(
            comment.encode('utf-8')).decode('utf-8')
        self.payment_info["comment"] = comment_base64
        await interaction.response.edit_message(
            embed=self.data[0]["to_pay_embed"].add_field(
                name="Комментарий к оплате: " if self.lang == "ru" else "Comment in payment: ",
                value=self.payment_info["comment"], inline=False).add_field(
                name="Сумма к оплате: " if self.lang == "ru" else "Summ in payment: ",
                value=self.payment_info["real_summ"], inline=False),
            view=PaymentButtons(payment_info=self.payment_info, lang=self.lang, member=interaction.user),
            delete_after=7200)

    ...


class VipButtons(nextcord.ui.View):
    def __init__(self, lang: str):
        super().__init__()
        self.lang = lang
        self.timeout = 300
        self.payment_info: dict = {
            'real_summ': None,
            'enrollment_summ': None,
            'comment': None,
            'type': "vip"
        }
        self.data = [{
            "one_month": "Один месяц 30 RUB",
            "six_month": "Шесть месяцев 182 RUB",
            "one_year": "Один год 364 RUB",
            "to_pay": "Перейти к оплате",
            "to_pay_embed": deepcopy(payment_ru_embed)
        }, None] if self.lang == "ru" else [{
            "one_month": "One month 30 RUB",
            "six_month": "Six month 182 RUB",
            "one_year": "One year 364 RUB",
            "to_pay": "Move o pay",
            "to_pay_embed": deepcopy(payment_en_embed)
        }, None]
        self.to_pay.disabled, self.to_pay.label = True, self.data[0]["to_pay"]
        self.one_month.label = self.data[0]["one_month"]
        self.six_month.label = self.data[0]["six_month"]
        self.one_year.label = self.data[0]["one_year"]

    @staticmethod
    def update_buttons(button_dict: dict):
        for button, properties in button_dict.items():
            for property_name, value in properties.items():
                setattr(button, property_name, value)

    def disable_buttons(self, button: str):
        if button == "one_month":
            self.update_buttons({
                self.one_month: {"disabled": True, "style": nextcord.ButtonStyle.green},
                self.six_month: {"disabled": False, "style": nextcord.ButtonStyle.grey},
                self.one_year: {"disabled": False, "style": nextcord.ButtonStyle.grey},
                self.to_pay: {"disabled": False, "style": nextcord.ButtonStyle.green},
            })
        elif button == "six_month":
            self.update_buttons({
                self.one_month: {"disabled": False, "style": nextcord.ButtonStyle.grey},
                self.six_month: {"disabled": True, "style": nextcord.ButtonStyle.green},
                self.one_year: {"disabled": False, "style": nextcord.ButtonStyle.grey},
                self.to_pay: {"disabled": False, "style": nextcord.ButtonStyle.green},
            })
        elif button == "one_year":
            self.update_buttons({
                self.one_month: {"disabled": False, "style": nextcord.ButtonStyle.grey},
                self.six_month: {"disabled": False, "style": nextcord.ButtonStyle.grey},
                self.one_year: {"disabled": True, "style": nextcord.ButtonStyle.green},
                self.to_pay: {"disabled": False, "style": nextcord.ButtonStyle.green},
            })

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def one_month(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.payment_info['real_summ'] = 30.0
        self.payment_info['enrollment_summ'] = 30.0
        self.disable_buttons("one_month")
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def six_month(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.payment_info['real_summ'] = 182.0
        self.payment_info['enrollment_summ'] = 182.0
        self.disable_buttons("six_month")
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def one_year(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.payment_info['real_summ'] = 364.0
        self.payment_info['enrollment_summ'] = 364.0
        self.disable_buttons("one_year")
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def to_pay(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()
        comment = f"{interaction.user.id}:" + ''.join(random.choices(
            string.ascii_letters + string.digits + string.punctuation,
            k=10)).replace(':', '-')
        comment_base64 = base64.b64encode(
            comment.encode('utf-8')).decode('utf-8')
        self.payment_info["comment"] = comment_base64
        await interaction.response.edit_message(
            embed=self.data[0]["to_pay_embed"].add_field(
                name="Комментарий к оплате: " if self.lang == "ru" else "Comment in payment: ",
                value=self.payment_info["comment"], inline=False).add_field(
                name="Сумма к оплате: " if self.lang == "ru" else "Summ in payment: ",
                value=self.payment_info["real_summ"], inline=False),
            view=PaymentButtons(payment_info=self.payment_info, lang=self.lang, member=interaction.user),
            delete_after=7200)

    ...


class Dropdown(nextcord.ui.Select):
    def __init__(self, lang):
        self.emojies = {
            "white": "⬜:937593712391901184",
            "yellow": "🟨:937593431591641100",
            "green": "🟩:937593680750080030",
            "purple": "🟪:937593682620719164",
            "black": "⬛:939886116113350706",
            "orange": "🟧:939889190924075018",
            "blue": "🟦:939888364994330674",
            "brown": "🟫:939895587422208020",
            "dark_green": "❎:939892549995339807",
            "dark_red": "❎:1031504964708741190",
            "mint": "❎:937593699771220009",
            "super_black": "❎:1043491354296193115",
            "light_brown": "❎:939896208825151539",
            "light_green": "❎:939889611239456799",
            "soft_yellow": "❎:939894916165828679",
            "pink": "❎:939894014214287380",
            "bright_orange": "❎:939890731110240308",
            "pale_purplish_pink": "❎:1110220843960782979",
            "light_yellow": "❎:939890079424454736",
            "bright_red": "❎:939887236550377532",
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
            "dark_green": "Тёмно-зелёный",
            "dark_red": "Тёмно-красный",
            "mint": "Мятный",
            "super_black": "Супер-чёрный",
            "light_brown": "Светло-коричневый",
            "light_green": "Светло-зелёный",
            "soft_yellow": "Нежно-желтый",
            "pink": "Розовый",
            "bright_orange": "Ярко-оранжевый",
            "pale_purplish_pink": "Бледно-пурпурно-розовый",
            "light_yellow": "Светло-желтый",
            "bright_red": "Ярко-красный",
            "color": "Твой любимый цвет это...",
            "placeholder": "Выберите свой любимый цвет...",
            "interaction_removed": "Успешно удалён цвет",
            "interaction_added": "Успешно добавлен цвет",
            "error_msg": "У вас нет нужной роли! (VIP)",
        } if lang == "RU" else {
            "white": "White",
            "yellow": "Yellow",
            "green": "Green",
            "purple": "Purple",
            "black": "Black",
            "orange": "Orange",
            "blue": "Blue",
            "brown": "Brown",
            "dark_green": "Dark green",
            "dark_red": "Dark red",
            "mint": "Mint",
            "super_black": "Super black",
            "light_brown": "Light brown",
            "light_green": "Light green",
            "soft_yellow": "Soft yellow",
            "pink": "Pink",
            "bright_orange": "Bright orange",
            "pale_purplish_pink": "Pale purplish pink",
            "light_yellow": "Light yellow",
            "bright_red": "Bright red",
            "color": "Your favourite colour is ...",
            "placeholder": "Choose your favourite colour...",
            "interaction_removed": "Succesfully deleted colour",
            "interaction_added": "Succesfully added colour",
            "error_msg": "You don't have the right role! (VIP)",
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
            allower_roles_id = [junior_moderator, booster_role_id, vip_en_role_id, vip_ru_role_id]
            if not any(role_id in user_roles_id for role_id in allower_roles_id):
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
            print(ex_format(ex, "Dropdown_callback_roles"))


class MainButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, prevent_update=False)
        self.HELP_EN.disabled = True
    
    @nextcord.ui.button(
        label="ИНСТРУКЦИЯ",
        style=nextcord.ButtonStyle.green,
        custom_id="MainButtons:ИНСТРУКЦИЯ",
        row=0
    )
    async def HELP_RU(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            description="Для оплаты без комиссии используйте свой киви кошелёк. Для этого переводите" 
                        " на него нужную сумму по СБП и далее оплачиваете нужную услугу.")
        await interaction.send(embed=embed, ephemeral=True)

    @nextcord.ui.button(
        label="MANUAL",
        style=nextcord.ButtonStyle.green,
        custom_id="MainButtons:MANUAL",
        row=0
    )
    async def HELP_EN(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass

    @nextcord.ui.button(
        label="КУПИТЬ РЕКЛАМУ",
        style=nextcord.ButtonStyle.gray,
        custom_id="MainButtons:РЕКЛАМА",
        row=0
    )
    async def adver_ru(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        member = interaction.user
        await interaction.response.send_message(ephemeral=True,
                                                embed=deepcopy(
                                                    advertisement_ru_embed),
                                                view=AdvertisementButtons(lang="ru"))
        """
        120р один день если брать подневно
        Если брать пакетом на месяц 3000
        Зачисляется сумма большая чем сумма оплаты при покупки месяца
        """
        ...

    @nextcord.ui.button(
        label="ADVERTISEMENT",
        style=nextcord.ButtonStyle.gray,
        custom_id="MainButtons:ADVERTISEMENT",
        row=0
    )
    async def adver_en(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message(ephemeral=True,
                                                embed=deepcopy(
                                                    advertisement_en_embed),
                                                view=AdvertisementButtons(lang="en"))

    @nextcord.ui.button(
        label="VIP",
        style=nextcord.ButtonStyle.blurple,
        custom_id="MainButtons:VIP",
        row=0
    )
    async def vip(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        lang = "ru" if ru_role_id in [
            role.id for role in interaction.user.roles] else "en"
        await interaction.response.send_message(ephemeral=True,
                                                embed=deepcopy(vip_ru_embed) if lang == "ru"
                                                else deepcopy(vip_en_embed),
                                                view=VipButtons(lang=lang))
    
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
    
    @nextcord.ui.button(
        label="HELP",
        style=nextcord.ButtonStyle.red,
        custom_id="MainButtons:ticket_create"
    )
    async def ticket_create(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        lang = "ru" if ru_role_id in [
            role.id for role in interaction.user.roles] else "en"
        data = {
            "title": "Связь с администрацией"
        } if lang == "ru" else {
            "title": "Связь с администрацией"
        }
        ticket_modal = nextcord.ui.Modal(title=data["title"])
        ticket_modal.add_item(tranzaction_id := nextcord.ui.TextInput(
            label="Введите номер транзакции",
            placeholder="0123456789",
            required=True,
            min_length=9,
            max_length=20,
        ))
        ticket_modal.add_item(tranzaction_id := nextcord.ui.TextInput(
            label="Введите комментарий, который вы указали при оплате",
            placeholder="qwerty12345==",
            required=True,
            min_length=10,
        ))
        ticket_modal.add_item(tranzaction_id := nextcord.ui.TextInput(
            label="Опишите причину создания тикета",
            placeholder="Неверно указал комментарий, помогите",
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        ))
        async def modal_callback(interaction: nextcord.Interaction):
            pass # TODO
        #await interaction.response.send_modal(ticket_modal)
        if lang == "ru":
            await interaction.send("Создайте тикет, укажите номер транзакции, комменатрий, опишите ситуацию... https://discord.com/channels/691182902633037834/975319189407559691/1110882800841805846", ephemeral=True)
        else:
            await interaction.send("Create a ticket, specify the transaction number, comment, describe the situation... https://discord.com/channels/691182902633037834/975330313112780810/1110883199208407092", ephemeral=True)
                                   

class AuthPayWT(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.obj_guild = self.bot.get_guild(691182902633037834)
        self.on_init.start()
        self.check_roles_payment.start()
        self.bot.add_view(MainButtons())

    def __del__(self):
        ...

    @tasks.loop(count=1, reconnect=False)
    async def on_init(self):
        pass
 
    def cog_unload(self):
        self.bot.remove_view(MainButtons())
        self.check_roles_payment.cancel()

    @tasks.loop(hours=1)
    async def check_roles_payment(self):
        try:
            for data_path, type in zip([data_adver_path, data_vip_path],
                                        [[120.0, [adv_ru_role_id, adv_en_role_id]],
                                        [1.0, [vip_ru_role_id, vip_en_role_id]]]):
                with open(data_path, 'r') as data_file:
                    first_line = data_file.readline().strip()
                    other_lines = data_file.readlines()
                date_in_file = datetime.datetime.strptime(
                    first_line, '%Y-%m-%d').date()
                today = datetime.date.today()
                if date_in_file < today:
                    first_line = today.strftime('%Y-%m-%d') + '\n'
                    for i, line in enumerate(other_lines):
                        parts = line.strip().split(':')
                        new_enrollment_summ = float(parts[1]) - type[0]
                        if new_enrollment_summ > 0:
                            other_lines[i] = f"{parts[0]}:{new_enrollment_summ:.2f}\n"
                        else:
                            other_lines[i] = f"{parts[0]}:0:to_delete\n"
                            member = self.obj_guild.get_member(
                                int(parts[0]))
                            for _type in type[1]:
                                await member.remove_roles(self.obj_guild.get_role(_type))
                    with open(data_path, 'w') as data_file:
                        data_file.write(first_line)
                        data_file.writelines(
                            [line if "to_delete" not in line else "" for line in other_lines])
        except Exception as ex:
            print(ex_format(ex, "AuthCog"))

    @commands.command()
    async def paymentmsg(self, ctx: Context):
        if ctx.author.id not in self.bot.OWNERS:
            return
        await ctx.message.delete()
        await ctx.channel.send(
            embed=deepcopy(main_embed),
            view=MainButtons()
        )

def setup(bot: Bot) -> None:
    print("QiwiPay.py loaded")
    bot.add_view(MainButtons())
    bot.add_cog(AuthPayWT(bot))
