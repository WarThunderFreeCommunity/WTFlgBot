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

main_message_text = \
"""
```
Вы присоединились к Fan серверу War Thunder\n
You have joined the War Thunder Fan Server
```
```
Выберите свой язык нажав на кнопку:  Russian / Englich\n
Select your language by clicking on the button: Russian / Englich
```

Чтобы купить рекламу полка нажмите на кнопку. После оплаты подписки вам бот выдаст роль, которая даст вам возможность выкладывать рекламу в специальном канале <#955043080178909204> Если у вас другой вид рекламы то напишите главе сервера. Подробности в канале <#1095191673245532261>\n
To buy squadron ads, click on the button. After paying for the subscription, the bot will give you a role that will give you the opportunity to advertise in a special channel <#1085546330467872889> If you have a different type of advertising, then write to the head of the server <#1095191673245532261>

VIP - покупая подписку вы поддерживаете наш сервер в развитии и приобретаете дополнительные бонусы себе на нашем сервере. Подробности в канале <#1095191673245532261>\n
VIP - by purchasing a subscription, you support our server in development and purchase additional bonuses for yourself on our server. You can find out about this in the channel <#1095191673245532261>
"""

main_embed = nextcord.Embed.from_dict({
    "title": "Добро пожаловать на сервер wt",
    "description": main_message_text,
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
    "author": {
        "name": "yunik#4792",
        "url": "",
        "icon_url": "https://cdn.discordapp.com/avatars/286914074422280194/8f78a4313bc06862ce529291172edf8d.webp?"
                    "size=32",
    },
    "thumbnail": {"url": ""},
    "fields": [

    ],
    "image": {"url": ""},
    "footer": {
        "text": "Embed Footer",
        "icon_url": "",
    },
})

advertisement_ru_embed = nextcord.Embed.from_dict({
    "title": "Реклама",
    "description": "Выберите нужное значение",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
    "author": {
        "name": "yunik#4792",
        "url": "",
        "icon_url": "https://cdn.discordapp.com/avatars/286914074422280194/8f78a4313bc06862ce529291172edf8d.webp?"
                    "size=32",
    },
    "thumbnail": {"url": ""},
    "fields": [

    ],
    "image": {"url": ""},
    "footer": {
        "text": "Embed Footer",
        "icon_url": "",
    },
})

advertisement_en_embed = nextcord.Embed.from_dict({
    "title": "Advertisment",
    "description": "Select the desired value",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
    "author": {
        "name": "yunik#4792",
        "url": "",
        "icon_url": "https://cdn.discordapp.com/avatars/286914074422280194/8f78a4313bc06862ce529291172edf8d.webp?"
                    "size=32",
    },
    "thumbnail": {"url": ""},
    "fields": [

    ],
    "image": {"url": ""},
    "footer": {
        "text": "Embed Footer",
        "icon_url": "",
    },
})

vip_ru_embed = nextcord.Embed.from_dict({
    "title": "VIP",
    "description": "Выберите нужное значение",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
    "author": {
        "name": "yunik#4792",
        "url": "",
        "icon_url": "https://cdn.discordapp.com/avatars/286914074422280194/8f78a4313bc06862ce529291172edf8d.webp?"
                    "size=32",
    },
    "thumbnail": {"url": ""},
    "fields": [

    ],
    "image": {"url": ""},
    "footer": {
        "text": "Embed Footer",
        "icon_url": "",
    },
})

vip_en_embed = nextcord.Embed.from_dict({
    "title": "VIP",
    "description": "Select the desired value",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
    "author": {
        "name": "yunik#4792",
        "url": "",
        "icon_url": "https://cdn.discordapp.com/avatars/286914074422280194/8f78a4313bc06862ce529291172edf8d.webp?"
                    "size=32",
    },
    "thumbnail": {"url": ""},
    "fields": [

    ],
    "image": {"url": ""},
    "footer": {
        "text": "Embed Footer",
        "icon_url": "",
    },
})

payment_ru_embed = nextcord.Embed.from_dict({
    "title": "Оплата",
    "description": "Пожалуйста, укажите комментарий к платежу из данного сообщения",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
    "author": {
        "name": "yunik#4792",
        "url": "",
        "icon_url": "https://cdn.discordapp.com/avatars/286914074422280194/8f78a4313bc06862ce529291172edf8d.webp?"
                    "size=32",
    },
    "thumbnail": {"url": ""},
    "fields": [

    ],
    "image": {"url": ""},
    "footer": {
        "text": "Embed Footer",
        "icon_url": "",
    },
})

payment_en_embed = nextcord.Embed.from_dict({
    "title": "Payment",
    "description": "Please enter a comment on the payment from this message",
    "color": 0xE74C3C,
    "timestamp": datetime.datetime.now().isoformat(),
    "author": {
        "name": "yunik#4792",
        "url": "",
        "icon_url": "https://cdn.discordapp.com/avatars/286914074422280194/8f78a4313bc06862ce529291172edf8d.webp?"
                    "size=32",
    },
    "thumbnail": {"url": ""},
    "fields": [

    ],
    "image": {"url": ""},
    "footer": {
        "text": "Embed Footer",
        "icon_url": "",
    },
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
                    """
                    Добавить ограничение на вызов эфмеральных сообщений от ондого пользователя
                    """
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
                ("Что-то пошло не так. Пожалуйста создайте тикет. Укажите комментарий к платежу, сумму, роль,"
                " которую вы покупали. А также номер платежа. <#975319189407559691>" if self.lang == "ru" else
                "Something went wrong. Please create a ticket. Specify a comment on the payment, the amount,"
                " the role that you bought. As well as the payment number. <#975330313112780810>")
            )
        except BaseException as ex:
            from traceback import format_exception
            result = "".join(format_exception(ex, ex, ex.__traceback__))
            await interaction.channel.send(f"Exception:\n```bash\n{result.replace('```', '`')}\n```")

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
        self.payment_info['real_summ'] = 1 # 120.0
        self.payment_info['enrollment_summ'] = 120.0
        self.disable_buttons("one_day")
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def one_month(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.payment_info['real_summ'] = 1 # 3000.0
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
        self.payment_info['real_summ'] = 1 # 30.0
        self.payment_info['enrollment_summ'] = 30.0
        self.disable_buttons("one_month")
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def six_month(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.payment_info['real_summ'] = 1 # 182.0
        self.payment_info['enrollment_summ'] = 182.0
        self.disable_buttons("six_month")
        await interaction.response.edit_message(view=self)

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def one_year(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.payment_info['real_summ'] = 1 # 364.0
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


class MainButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, prevent_update=False)

    @nextcord.ui.button(
        label="RUSSIAN", style=nextcord.ButtonStyle.green, custom_id="MainButtons:russian"
    )
    async def russian(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        member, guild = interaction.user, interaction.guild
        role = guild.get_role(ru_role_id)
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message("Удалена RUSSIAN роль", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message("Добавлена RUSSIAN роль", ephemeral=True)

    @nextcord.ui.button(
        label="ENGLISH", style=nextcord.ButtonStyle.green, custom_id="MainButtons:ENGLISH"
    )
    async def english(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        member, guild = interaction.user, interaction.guild
        role = guild.get_role(en_role_id)
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message("Removed ENGLISH role", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message("Added ENGLISH role", ephemeral=True)

    @nextcord.ui.button(
        label="РЕКЛАМА", style=nextcord.ButtonStyle.gray, custom_id="MainButtons:РЕКЛАМА"
    )
    async def adver_ru(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        member = interaction.user
        await interaction.response.send_message(ephemeral=True,
                                                embed=deepcopy(
                                                    advertisement_ru_embed),
                                                view=AdvertisementButtons(lang="ru"))
        """
        120р один день если брать подневно
        Если брать пакетом на месяц 3000к
        Зачисляется сумма большая чем сумма оплаты при покупки месяца
        """
        ...

    @nextcord.ui.button(
        label="ADVERTISEMENT", style=nextcord.ButtonStyle.gray, custom_id="MainButtons:ADVERTISEMENT"
    )
    async def adver_en(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message(ephemeral=True,
                                                embed=deepcopy(
                                                    advertisement_en_embed),
                                                view=AdvertisementButtons(lang="en"))
        """
        ...
        """
        ...

    @nextcord.ui.button(
        label="VIP", style=nextcord.ButtonStyle.blurple, custom_id="MainButtons:VIP"
    )
    async def vip(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        lang = "ru" if ru_role_id in [
            role.id for role in interaction.user.roles] else "en"
        await interaction.response.send_message(ephemeral=True,
                                                embed=deepcopy(vip_ru_embed) if lang == "ru"
                                                else deepcopy(vip_en_embed),
                                                view=VipButtons(lang=lang))
        """
        месяц 30 рублей,
        пол года 182 рубля,
        год 364 рубля
        """
        ...

    ...


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

    @tasks.loop(seconds=1)
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
                    first_line = "2022-05-05\n"#today.strftime('%Y-%m-%d') + '\n'
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
        except Exception as exception:
            print(exception)

    @commands.command()
    async def pymsg(self, ctx: Context, ):
        if ctx.author.id not in self.bot.OWNERS:
            return
        try:
            self.bot.DATA['messages']['pymsg']
        except KeyError:
            self.bot.DATA['messages']['pymsg'] = None
        await ctx.message.delete()
        if not self.bot.DATA['messages']['pymsg']:
            self.bot.DATA['messages']['pymsg'] = await ctx.channel.send(
                embed=deepcopy(main_embed),
                view=MainButtons()
            )
            return
        await self.bot.DATA['messages']['pymsg'].edit(
            embed=deepcopy(main_embed),
            view=MainButtons()
        )


def setup(bot: Bot) -> None:
    print("QiwiPay.py loaded")
    bot.add_view(MainButtons())
    bot.add_cog(AuthPayWT(bot))
