import time
import json
import asyncio
import re
from typing import List

import nextcord
from nextcord.ext import tasks, application_checks
from nextcord.ext.commands import Bot, Cog

from ..extensions.DBWorkerExtension import DataBase
from ..extensions.EXFormatExtension import ex_format


TECH_IDS = None
NATION_IDS = None
RU_ROLE_ID: int = 795232311477272576
EN_ROLE_ID: int = 795232315579564032
VIP_RU_ROLE_ID = 1007965606789783572
VIP_EN_ROLE_ID = 1085530065707733012


class AfterKickUserButtons(nextcord.ui.View):
    def __init__(self, lang, members, message) -> None:
        super().__init__(timeout=5*60)
        self.members = members
        self.message = message
        self.data = { # TODO translate
            ...
        } if lang == "RU" else { 
            ...
        }
        self.close_for_all.label = "close_for_all"
        self.close_for_user.label = "close_for_user"

        self.close_for_all.disabled = True # TODO button_easy
        self.close_for_user.disabled = True # TODO button_easy

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def close_for_all(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("close_for_all")
        ...
    
    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def close_for_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("close_for_user")
        ...

    async def on_timeout(self):
        self.close_for_all.disabled = True
        self.close_for_user.disabled = True
        try:
            await self.message.edit(view=self)     
        except BaseException:
            pass


# TODO переписать на один класс и два наследника (делать в последнюю очередь)
class ChooseGameModeSelect(nextcord.ui.Select):
    def __init__(self, admins, lang):
        self.admins = admins
        self.lang = lang
        self.data = {
            "options_clear": "Очистить выбор",
        } if self.lang == "RU" else {
            "options_clear": "Clear selection",
        }
        options = [
            nextcord.SelectOption(
                label="Танковые",
                description="Выбрать танковые бои",
                value=0
            ),
            nextcord.SelectOption(
                label="Воздушные",
                description="Выбрать воздушные бои",
                value=1
            ),
            nextcord.SelectOption(
                label="Морские",
                description="Выбрать морские бои",
                value=2
            ),
            nextcord.SelectOption(
                label="Вертолётные",
                description="Выбрать вортолётные бои",
                value=3
            ),
            nextcord.SelectOption(
                label="Убрать режим",
                description="Убрать режим игры...",
                value='-'
            )
        ]
        super().__init__(
            placeholder="Выберите режим игры..",
            min_values=1, 
            max_values=1,
            options=options,
            row=0
        )

    async def callback(self, interaction: nextcord.Interaction):
        if interaction.user.id not in self.admins \
        and not interaction.user.guild_permissions.administrator:
            await interaction.send(self.data["no_admin"], ephemeral=True)
            return
        try:
            db = DataBase("WarThunder.db")
            await db.connect()
            await db.run_que(
                "UPDATE VoiceCogChannelsSaves SET techId=? WHERE creatorId=?",
                (None if self.values[0] == '-' else self.values[0] , interaction.user.id)
            )
            self.view.rename_channel.disabled = False
            self.view.changed_names.append("tech")
            await self.view.update_message()
            await interaction.send(
                "Настройки сохранены, не забудьте применить их для данного канала!\n" \
                "Будьте внимательны, настройки можно применить раз в пять минут к одному каналу.\n" \
                "Если вы не хотите ждать, можете просто пересоздать канал, ограничение идёт со стороны "\
                "Discord'а",
                ephemeral=True
            )
        except BaseException as ex:
            print(ex_format(ex, "ChooseGameModeSelect.callback"))
            await interaction.send(f"Что то пошло не так", ephemeral=True)
        finally:
            await db.close()


class ChooseGameNationSelect(nextcord.ui.Select):
    def __init__(self, admins, lang):
        self.admins = admins
        self.lang = lang
        # TODO доделать перевод :)
        self.data = {
            "options_clear": "Очистить выбор",
            "label_usa": "Америка",
            "description_usa": "Выбрать Америку",
            "label_ussr": "Советский союз",
            "description_ussr": "Выбрать Советский союз",
            "label_japan": "Япония",
            "description_japan": "Выбрать Японию",
            "remove_mode": "Убрать режим...",
            "description_mode": "Убрать режим игры...",
        } if self.lang == "RU" else {
            "options_clear": "Clear selection",
            "label_usa": "USA",
            "description_usa": "Choose USA",
            "label_ussr": "USSR",
            "description_ussr": "Choose USSR",
            "label_japan": "Japan",
            "description_japan": "Choose Japan",
            "remove_mode": "Remove mode...",
            "description_mode": "Remove game mode...",
        }
        options = [
            nextcord.SelectOption(
                label=self.data["label_usa"],
                description=self.data["description_usa"],
                value=0
            ),
            nextcord.SelectOption(
                label=self.data["label_ussr"],
                description=self.data["description_ussr"],
                value=1
            ),
            nextcord.SelectOption(
                label=self.data["label_japan"],
                description=self.data["description_japan"],
                value=2
            ),
            nextcord.SelectOption(
                label="Германия",
                description="-",
                value=3
            ),
            nextcord.SelectOption(
                label="Великобритания",
                description="-",
                value=4
            ),
            nextcord.SelectOption(
                label="Италия",
                description="-",
                value=5
            ),
            nextcord.SelectOption(
                label="Франция",
                description="-",
                value=6
            ),
            nextcord.SelectOption(
                label="Китай",
                description="-",
                value=7
            ),
            nextcord.SelectOption(
                label="Швеция",
                description="-",
                value=8
            ),
            nextcord.SelectOption(
                label="Израиль",
                description=self.data["description_japan"],
                value=9
            ),
            nextcord.SelectOption(
                label=self.data["remove_mode"],
                description="-",
                value='-'
            )# TODO translate
        ]
        super().__init__(
            placeholder="Выберите нацию игры..",
            min_values=1, 
            max_values=1,
            options=options,
            row=1
        )

    async def callback(self, interaction: nextcord.Interaction):
        if interaction.user.id not in self.admins \
        and not interaction.user.guild_permissions.administrator:
            await interaction.send(self.data["no_admin"], ephemeral=True)
            return
        try:
            db = DataBase("WarThunder.db")
            await db.connect()
            await db.run_que(
                "UPDATE VoiceCogChannelsSaves SET nationId=? WHERE creatorId=?",
                (None if self.values[0] == '-' else self.values[0] , interaction.user.id)
            )
            self.view.rename_channel.disabled = False
            self.view.changed_names.append("nation")
            await self.view.update_message()
            await interaction.send(
                "Настройки сохранены, не забудьте применить их для данного канала!\n" \
                "Будьте внимательны, настройки можно применить раз в пять минут к одному каналу.\n" \
                "Если вы не хотите ждать, можете просто пересоздать канал, ограничение идёт со стороны "\
                "Discord'а",
                ephemeral=True
            )
        except BaseException as ex:
            print(ex_format(ex, "ChooseGameModeSelect.callback"))
            await interaction.send(f"Что то пошло не так", ephemeral=True)
        finally:
            await db.close()



class KickUserSelect(nextcord.ui.Select):
    def __init__(self, admins, members, lang):
        self.admins = admins
        self.members = members
        self.lang = lang
        self.data = {
            "options_descr": "Удалить из канала ",
            "options_clear": "Очистить выбор",
            "placeholder": "Выберите человека, которого нужно кикнуть...",
            "no_admin": "Вы не являяетесь администратором",
            "answer": "Из канала удалены:\n",
            "none_answer": "Никто не удалён..."
        } if self.lang == "RU" else {
            "options_descr": "Remove from Channel ",
            "options_clear": "Clear selection",
            "placeholder": "Choose the person you want to kick...",
            "no_admin": "You are not an administrator",
            "answer": "Removed from the channel:\n",
            "none_answer": "No one has been deleted..."
        }
        options = [
            nextcord.SelectOption(
                label=member.name,
                description=self.data["options_descr"] + member.name,
                value=member.id,
                emoji="❌" if member.id in admins else "✅"
            ) for member in members
        ]
        options.append(nextcord.SelectOption(
            label=self.data["options_clear"], value="clear")
        )
        super().__init__(
            placeholder=self.data["placeholder"],
            min_values=1, 
            # len(members) if len(members) > 0 else 1  # Просто перестраховка
            max_values=len(members),
            options=options,
            row=4
        )


    async def callback(self, interaction: nextcord.Interaction):
        if "clear" in self.values:
            self.values.remove("clear")
        if not self.values:
            return
        if interaction.user.id not in self.admins \
        and not interaction.user.guild_permissions.administrator:
            await interaction.send(self.data["no_admin"], ephemeral=True)
            return
        answer = self.data["answer"]
        members = []
        for member_id in self.values:
            if int(member_id) in self.admins:
                continue
            member = [
                member for member in self.members if int(member_id) == member.id
            ][0]
            members.append(member)
            answer += f"{member.name}\n"
            await member.move_to(None)
        if answer == self.data["answer"]:
            answer = self.data["none_answer"]
        message = await interaction.send(answer, ephemeral=True)
        await message.edit(view=AfterKickUserButtons(self.lang, members, message))


class VoiceInfoEmbed(nextcord.Embed):
    def __init__(self, lang, admins, channel: nextcord.VoiceChannel):
        # TODO translate
        self.data = {
            "user_designation": "Учатник ",
            "admin": "с правами администратора:",
            "not_admin": "без прав администратора:",
        } if lang == "RU" else {
            "user_designation": "Member ",
            "admin": "with administrator rights:",
            "not_admin": "without administrator rights:",
        }
        super().__init__(
            colour=nextcord.Colour.red(),
            title=channel.name.replace("●", ""),
        )
        for member in channel.members:
            self.add_field(
                name=self.data["user_designation"] + (self.data["admin"] \
                    if member.id in admins else self.data["not_admin"]),
                value=f"{member.mention};"
            )


class VoiceChannelsButtons(nextcord.ui.View):
    def __init__(self, lang, admin, message, channel):
        super().__init__(timeout=None)
        self.channel = channel
        self.message = message
        self.admins = [admin.id]
        self.changed_names = []
        self.lang = lang
        self.data = {
            "set_cmbr": "Установить боевой рейтинг",
            "set_tech": "Установить нацию игры",
            "set_limit": "Установить лимит пользователей",
            "rename_channel": "Применить изменения",
            "close_channel": "Закрыть канал",
            "open_channel": "Открыть канал",
            "add_member": "Добавить людей в закрытый канал",
            "del_member": "Удалить людей из закрытого канала",
            "set_limit_modal_name": "Установите лимит участников",
            "set_limit_modal_input": 'Лимит...',
            "after_limit_message": "Лимит установлен на: ",
            "after_limit_error": "Максимум 99, 0 для удаления ограничения",
            "else_error": "Что-то пошло не так...",
        } if lang == "RU" else {
            "set_cmbr": "Set combat rating",
            "set_tech": "Set game nation",
            "set_limit": "Set limit users",
            "rename_channel": "Accept changes",
            "close_channel": "Close channel",
            "open_channel": "Open channel",
            "add_member": "Add people to closed channel",
            "del_member": "Remove people from closed channel",
            "set_limit_modal_name": "Set limit of members",
            "set_limit_modal_input": "Limit...",
            "after_limit_message": "Limit set to: ",
            "after_limit_error": "Maximum of 99, 0 to remove the restriction",
            "else_error": "Something went wrong"
        }
        self.add_item(
            ChooseGameModeSelect(self.admins, self.lang)
        )
        self.add_item(
            ChooseGameNationSelect(self.admins, self.lang)
        )
        self.select = KickUserSelect(
            self.admins, self.channel.members, self.lang
        )
        self.add_item(self.select)
        self.set_cmbr.label = self.data["set_cmbr"]
        self.set_limit.label = self.data["set_limit"]
        self.rename_channel.label = self.data["rename_channel"]
        self.change_connect_rules.label = self.data["close_channel"]
        self.add_member.label = self.data["add_member"]
        self.del_member.label = self.data["del_member"]
        self.rename_channel.disabled = True # так и должно быть!
        self.channel_closed = False

    @staticmethod
    async def __check_timeout(channel_id):
        """Проверяет timeout дискорда на переименование каналов

        Args:
            channel_id (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            db = DataBase("WarThunder.db")
            await db.connect()
            last_time = (await db.get_one(
                "SELECT commandTime FROM VoiceCogChannels WHERE channelId=?",
                (channel_id,)
            ))[0]
            if not last_time or ((int(time.time()) - last_time) > 60*5):
                await db.run_que(
                    "UPDATE VoiceCogChannels SET commandTime=? WHERE channelId=?",
                    (int(time.time()), channel_id)
                )
                await db.close()
                return True, None
            else:
                await db.close()
                return False, 60*5 - (int(time.time()) - last_time)
        except BaseException as ex:
            print(ex_format(ex, "__check_timeout"))
            await db.close()

    async def update_message(self, member = None, pos = None, other = None, names: List[str] = None):
        # Вызывается при изменении on_voice_state_update для канала с данным сообщением
        try:
            db = DataBase("WarThunder.db")
            await db.connect()

            # Новый человек в канале
            if pos == "in":
                # TODO чекнуть if member т.к. там скорее всего обновляется то, что может тут.
                # тут слишком мало, что то забыл 💀
                ...
            
            # Человек вышел
            if pos == "out":
                # тут слишком мало, что то забыл xD
                if member.id in self.admins and len(self.admins) == 1:
                    self.rename_channel.disabled = False
                    self.admins.remove(member.id)
                    self.admins.append(self.channel.members[0].id)
                    await db.run_que(
                        "UPDATE VoiceCogChannels SET creatorId=? WHERE creatorId=?",
                        (self.channel.members[0].id, member.id)
                    )
                ...
            
            # Обновление имени 
            if pos == "name_update":
                try:
                    channel_settings = await db.get_one(
                        "SELECT techId, nationId, cmbrVar FROM VoiceCogChannelsSaves WHERE creatorId=?",
                        (other["interaction"].user.id,)
                    )
                    tech = TECH_IDS[str(channel_settings[0])] if channel_settings[0] != None else TECH_IDS['-'] 
                    nation = NATION_IDS[str(channel_settings[1])] if channel_settings[1] != None else NATION_IDS['-'] 
                    cmbr = channel_settings[2] if channel_settings[2] else TECH_IDS['-'] 
                    channel_name = \
                        f"● {nation if 'nation' in names else self.channel.name.split(' ')[1]} " \
                        f"{tech if 'tech' in names else self.channel.name.split(' ')[2]} " \
                        f"{self.channel.name.split(' ')[3]} {cmbr if 'cmbr' in names else self.channel.name.split(' ')[4]}"
                    await self.channel.edit(name=channel_name)
                    self.rename_channel.disabled = True
                except BaseException as ex:
                    print(ex_format(ex, "update_message -> name_update"))
            
            if member:
                self.remove_item(self.select)
                self.select = KickUserSelect(
                    self.admins, self.channel.members, self.lang
                )
                self.add_item(self.select)
            
            embed = VoiceInfoEmbed(self.lang, self.admins, self.channel)
            await self.message.edit(embed=embed, view=self)

        except BaseException as ex:
            print(ex_format(ex, "update_message"))
        finally:
            await db.close()

    async def check_admin_rules(self, interaction: nextcord.Interaction):
        if interaction.user.id in self.admins \
        or interaction.user.guild_permissions.administrator:
            return True
        await interaction.send("Вы не администратор", ephemeral=True)
        return False
    
    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.green, row=2)
    async def set_cmbr(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Установка БР для голосового
        """
        if not await self.check_admin_rules(interaction):
            return
        try:
            modal_cmbr = nextcord.ui.Modal(
                title="Выбор боевого рейтинга",
                timeout=5*60,
            )
            modal_cmbr.add_item(command_br := nextcord.ui.TextInput(
                label="Введите боевой рейтинг",
                placeholder='5.3',
                max_length=4,
                required=True,
            ))
            async def modal_callback(interaction: nextcord.Interaction):
                await interaction.response.defer(ephemeral=True, with_message=True)
                try:
                    if command_br.value not in ["0", "-"]:
                        pattern = r"^\d{1,2}\.\d$"
                        result = re.match(pattern, str(command_br.value))
                        if not result:
                            await interaction.send(f"Вы ввели неверное значение: {command_br.value}, пример верного: 10.3. '0' или '-' чтобы убрать", ephemeral=True)
                            return
                        true_nums = int(command_br.value.split(".")[0]) in range(1, 12+1) and int(command_br.value.split(".")[1]) in [0, 3, 7]
                        if not true_nums:
                            await interaction.send(f"Такого бр не существует!: {command_br.value}, пример верного: 6.7. '0' или '-' чтобы убрать", ephemeral=True)
                            return
                        cmbr_value = float(command_br.value)
                    else:
                        cmbr_value = None
                    db = DataBase("WarThunder.db")
                    await db.connect()
                    await db.run_que(
                        "UPDATE VoiceCogChannelsSaves SET cmbrVar=? WHERE creatorId=?",
                        (cmbr_value, interaction.user.id)
                    )
                    await interaction.send(
                        "Настройки сохранены, не забудьте применить их для данного канала!\n" \
                        "Будьте внимательны, настройки можно применить раз в пять минут к одному каналу.\n" \
                        "Если вы не хотите ждать, можете просто пересоздать канал, ограничение идёт со стороны "\
                        "Discord'а",
                        ephemeral=True
                    )
                    self.changed_names.append("cmbr")
                    self.rename_channel.disabled = False
                    await self.message.edit(view=self)
                except BaseException as ex:
                    ex = ex_format(ex, "set_cmbr_modal_ex")
                    await interaction.send(f"Что-то пошло не так!\nEx: ```{ex}```", ephemeral=True)
                    print(ex)
                finally:
                    await db.close()
                    
            modal_cmbr.callback = modal_callback
            await interaction.response.send_modal(modal_cmbr)
        except BaseException as ex:
            print(ex_format(ex, "set_cmbr_func"))

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.green, row=2)
    async def set_limit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Установка лимита пользователей
        """
        if not await self.check_admin_rules(interaction):
            return
        modal = nextcord.ui.Modal(self.data["set_limit_modal_name"])
        modal.add_item(
            limit := nextcord.ui.TextInput(
                label=self.data["set_limit_modal_input"],
                default_value=4
            )
        )
        async def modal_callback(interaction: nextcord.Interaction):
            try:
                db = DataBase("WarThunder.db")
                await db.connect()
                if int(limit.value) < 99:
                    await interaction.channel.edit(user_limit=int(limit.value))
                    await interaction.send(
                        str(self.data["after_limit_message"] + limit.value),
                        ephemeral=True
                    )
                    await db.run_que(
                        "UPDATE VoiceCogChannelsSaves SET limitVar=? WHERE creatorId=?",
                        (int(limit.value), interaction.user.id)
                    )
                else:
                    await interaction.send(self.data["after_limit_error"], ephemeral=True)
            except BaseException:
                await interaction.send(self.data["else_error"], ephemeral=True)
            finally:
                await db.close()
        modal.callback = modal_callback
        await interaction.response.send_modal(modal)
    
    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey, row=2)
    async def rename_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Применяет изменения имени (можно использоавать раз в пять минут)
        """
        if not await self.check_admin_rules(interaction):
            return
        permission, period = await self.__check_timeout(interaction.channel.id)
        if not permission:
            await interaction.send(
                f"Discord timeout error, please wait {round(period/60, 1)} minutes",
                ephemeral=True
            )
            return
        button.disabled = True
        await self.update_message(pos="name_update", other={"interaction": interaction}, names=self.changed_names)
        await interaction.send("Настройки применены к каналу!", ephemeral=True)

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.blurple, row=3)
    async def change_connect_rules(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Закрывает чат для вступления других людей (только премиум)
        """
        try:
            if not await self.check_admin_rules(interaction):
                return
            roles_id = [role.id for role in interaction.user.roles]
            if VIP_RU_ROLE_ID not in roles_id and VIP_EN_ROLE_ID not in roles_id and not interaction.user.guild_permissions.administrator:
                await interaction.send("У вас нет роли VIP! Тут вы можете её приобрести: https://discord.com/channels/691182902633037834/1012522502230114374/1128956079229894707", ephemeral=True)
                return
            channel = interaction.channel
            ru_role = interaction.guild.get_role(RU_ROLE_ID)
            en_role = interaction.guild.get_role(EN_ROLE_ID)
            if not self.channel_closed:
                overwrite = nextcord.PermissionOverwrite()
                overwrite.view_channel = True
                overwrite.connect = False
                await channel.set_permissions(ru_role, overwrite=overwrite)
                await channel.set_permissions(en_role, overwrite=overwrite)
                for member in channel.members:
                    overwrite.connect = True
                    overwrite.stream = True
                    overwrite.send_messages = True
                    overwrite.attach_files = True
                    overwrite.embed_links = True
                    overwrite.add_reactions = True
                    overwrite.read_message_history = True
                    await channel.set_permissions(member, overwrite=overwrite)
                button.label = self.data["open_channel"]
                await interaction.send("Канал закрыт для вступления!", ephemeral=True)
            else:
                await channel.edit(sync_permissions=True)
                button.label = self.data["close_channel"]
                await interaction.send("Канал открыт для вступления!", ephemeral=True)
            self.channel_closed = not self.channel_closed   
            await self.message.edit(view=self)
        except BaseException as ex:
            print(ex_format(ex, "change_connect_rules_voice_cog"))

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.blurple, row=3)
    async def add_member(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Добавление людей в права канала (только премиум)
        """
        try:
            if not await self.check_admin_rules(interaction):
                return
            roles_id = [role.id for role in interaction.user.roles]
            if VIP_RU_ROLE_ID not in roles_id and VIP_EN_ROLE_ID not in roles_id and not interaction.user.guild_permissions.administrator:
                await interaction.send("У вас нет роли VIP! Тут вы можете её приобрести: https://discord.com/channels/691182902633037834/1012522502230114374/1128956079229894707", ephemeral=True)
                return
            modal_add = nextcord.ui.Modal(
                title="Добавить доступ к каналу",
                timeout=5*60,
            )
            modal_add.add_item(member_id := nextcord.ui.TextInput(
                label="Введите id человека для добавления доступа",
                placeholder="404512224837894155",
                required=True,
            ))
            async def modal_callback(interaction: nextcord.Interaction):
                try:
                    if member_id.value.isdigit():
                        member = nextcord.utils.get(interaction.guild.members, id=int(member_id.value))
                        channel = interaction.channel

                        overwrite = nextcord.PermissionOverwrite()
                        overwrite.connect = True
                        await channel.set_permissions(member, overwrite=overwrite)
                    else:
                        await interaction.send("Введите правильный Id пользователя, состоящий только из цифр", ephemeral=True)
                except BaseException as ex:
                    print(ex_format(ex, "add_member_callback"))
            modal_add.callback = modal_callback
            await interaction.response.send_modal(modal_add)
        except BaseException as ex:
            print(ex_format(ex, "add_member_button"))
        
    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.blurple, row=3)
    async def del_member(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Удаление людей в правах канала (только премиум)
        """
        try:
            if not await self.check_admin_rules(interaction):
                return
            roles_id = [role.id for role in interaction.user.roles]
            if VIP_RU_ROLE_ID not in roles_id and VIP_EN_ROLE_ID not in roles_id and not interaction.user.guild_permissions.administrator:
                await interaction.send("У вас нет роли VIP! Тут вы можете её приобрести: https://discord.com/channels/691182902633037834/1012522502230114374/1128956079229894707", ephemeral=True)
                return
            modal_remove = nextcord.ui.Modal(
                title="Удалить доступ к каналу",
                timeout=5*60,
            )
            modal_remove.add_item(member_id := nextcord.ui.TextInput(
            label="Введите id человека для удаления доступа",
            placeholder="404512224837894155",
            required=True,
            ))
            async def modal_callback(interaction: nextcord.Interaction):
                try:
                    if member_id.value.isdigit():
                        member = nextcord.utils.get(interaction.guild.members, id=int(member_id.value))
                        channel = interaction.channel
                        overwrite = nextcord.PermissionOverwrite()
                        overwrite.connect = False
                        await channel.set_permissions(member, overwrite=overwrite)
                    else:
                        await interaction.send("Введите правильный Id пользователя, состоящий только из цифр", ephemeral=True)
                except BaseException as ex:
                    await interaction.send("Ой, какая то ошибка!", ephemeral=True)
                    print(ex_format(ex, "del_member_callback"))
            modal_remove.callback = modal_callback
            await interaction.response.send_modal(modal_remove)
        except BaseException as ex:
            print(ex_format(ex, "add_member_button"))



class VoiceCog(Cog):
    def __init__(self, bot: Bot):
        """_summary_

        Args:
            bot (Bot): _description_
        """
        self.bot = bot
        self.channel_views = {}
        self.smiles_channel = None
        self.afk_channel_id = None
        self.parrent_channel_ids = None
        self.tech_ids = None
        self.nation_ids = None
        self.update_consts.start()
        self.on_init.start()
    
    @tasks.loop(count=1, reconnect=False)
    async def on_init(self):
        # Чекер активных каналов
        try:
            db = DataBase("WarThunder.db")
            await db.connect()
            channels_db = await db.get_all("SELECT * FROM VoiceCogChannels")
            for channel_db in channels_db:
                try:
                    voice_channel: nextcord.VoiceChannel = await self.bot.fetch_channel(channel_db[1])
                except nextcord.errors.NotFound:
                    await db.run_que("DELETE FROM VoiceCogChannels WHERE channelId=?", (channel_db[1],))
                    continue
                if len(voice_channel.members) == 0:
                    await voice_channel.delete()
                    await db.run_que("DELETE FROM VoiceCogChannels WHERE channelId=?", (voice_channel.id,))
                    continue
                if channel_db[2] not in [member.id for member in voice_channel.members]:
                    await db.run_que(
                        "UPDATE VoiceCogChannels SET creatorId=? WHERE creatorId=?",
                        (channel_db[2], voice_channel.members[0])
                    )
                try:
                    message = await voice_channel.fetch_message(channel_db[4])
                except nextcord.errors.NotFound:
                    message = await voice_channel.send("creating new message...")
                    await db.run_que( # Можно на всякий указать id канала, но и так норм
                        "UPDATE VoiceCogChannels SET messageId=? WHERE messageId=?",
                        (message.id, channel_db[4])
                    )
                lang = self.parrent_channel_ids[str(channel_db[0])].split(":")[0]
                view = VoiceChannelsButtons(lang, voice_channel.members[0], message, voice_channel)
                embed = VoiceInfoEmbed(lang, [voice_channel.members[0].id], voice_channel)
                await message.edit(embed=embed, view=view)
                self.channel_views[voice_channel.id] = view
       
        except BaseException as ex:
            print(ex_format(ex, "on_init"))
        finally:
            await db.close()

    def cog_unload(self):
        pass

    @tasks.loop(hours=24)
    async def update_consts(self):
        """Обновляет данные поля раз в сутки:
        * self.smiles_channel = None
        * self.afk_channel_id = Nonation_idsself.update_messagene
        * self.parrent_channel_ids = None
        """
        try:
            db = DataBase("WarThunder.db")
            await db.connect()
            for constant in [
                "smiles_channel", 
                "afk_channel_id",
                "parrent_channel_ids",
                "tech_ids",
                "nation_ids"
            ]:
                temp = await db.get_one(
                    "SELECT constantValue FROM VoiceCogConstants WHERE constantName=?",
                    (constant,),
                )
                setattr(self, constant, json.loads(temp[0]))
        except BaseException as ex:
            print(ex_format(ex, "update_consts"))
        finally:
            global TECH_IDS
            global NATION_IDS
            TECH_IDS = self.tech_ids
            NATION_IDS = self.nation_ids
            await db.close()

    @Cog.listener()
    async def on_voice_state_update(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ): # TODO: Всё это дело можно разнести по разным функциям, дабы не городить 100500 вложенностей
        if before.channel == after.channel:
            return
        try:
            voice_channel = None
            db = DataBase("WarThunder.db")
            await db.connect()

            # Connected to creater new channel (channel with ➕ in name)
            if after.channel and (str(after.channel.id) in self.parrent_channel_ids):
                channel_type = self.parrent_channel_ids[str(after.channel.id)].split(':')
                channel_category = nextcord.utils.get(
                    member.guild.categories, id=int(channel_type[3])
                )
                afk_channel = nextcord.utils.get(
                    member.guild.voice_channels, id=int(self.afk_channel_id)
                )
                # Костыль для того, чтоб очумелые ручки не успевали выходить из канала до создания нового
                await member.move_to(afk_channel)
                tech_id = nation_id = cmbr_var = limit_var = None
                channel_options = self.parrent_channel_ids[str(after.channel.id)].split(":")
                lang = channel_options[0]
                if channel_type[4] == "-":
                    if not (channel_save_data := await db.get_one(
                            "SELECT * FROM VoiceCogChannelsSaves WHERE creatorId=?",
                            (member.id,)
                        )):
                        await db.run_que(
                            "INSERT INTO VoiceCogChannelsSaves (creatorId) VALUES (?)",
                            (member.id,)
                        )
                        channel_name = f"● - - {channel_options[1]} -"
                    else:
                        limit_var = channel_save_data[4] # user_limit
                        channel_name = \
                            f"{self.nation_ids[str(channel_save_data[2])] if channel_save_data[2] != None  else '● -'} " \
                            f"{self.tech_ids[str(channel_save_data[1])] if channel_save_data[1] != None  else '-'} " \
                            f"{channel_options[1]} {channel_save_data[3] if channel_save_data[3] != None else '-'}"
                else:
                    channel_name = f"● - {TECH_IDS[channel_type[4]]} {channel_options[1]} -"


                
                voice_channel = await member.guild.create_voice_channel(
                    name=channel_name,
                    #position=position,  # создаём канал под последним по времени
                    category=channel_category,  # в категории канала "основы"
                    reason=f"{member.name} in '{after.channel.name}'",  # (отображается в Audit Log)
                    user_limit= 0 if not limit_var else limit_var
                )
                await member.move_to(voice_channel)
                await voice_channel.edit(sync_permissions=True)
                message = await voice_channel.send(f"{member.mention} created voice")
                view = VoiceChannelsButtons(lang, member, message, voice_channel)
                embed = VoiceInfoEmbed(lang, [member.id], voice_channel)
                await message.edit(
                    content=f"{member.mention} created voice\nread instructions: "
                        "https://discord.com/channels/691182902633037834/813575222288187454/1129024795523153930",
                    embed=embed,
                    view=view
                )
                self.channel_views[voice_channel.id] = view
                await db.run_que(
                    "INSERT INTO VoiceCogChannels (parrentId, channelId, creatorId, channelTime, messageId) \
                        VALUES (?, ?, ?, ?, ?)",
                    (after.channel.id, voice_channel.id, member.id, int(time.time()), message.id)
                )

            # Disconected from created channel
            query = "SELECT channelId FROM VoiceCogChannels"
            created_channels = [x[0] for x in await db.get_all(query)]
            if before.channel and (before.channel.id in created_channels) \
            and len(before.channel.members) == 0: # Канал стал пустым, view обновляются автоматически!
                    await before.channel.delete()
                    await db.run_que(
                        "DELETE FROM VoiceCogChannels WHERE channelId=?",
                        (before.channel.id,)
                    )
                    del self.channel_views[before.channel.id]

            # Updating view in channel
            if before.channel and before.channel.id in self.channel_views:
                await self.channel_views[before.channel.id].update_message(member=member, pos="out")
            if after.channel and after.channel.id in self.channel_views:
                await self.channel_views[after.channel.id].update_message(member=member, pos="in")

        except BaseException as ex:
            if voice_channel:
                await voice_channel.delete()
            print(ex_format(ex, "on_voice_state_update in VoceCog"))
        finally:
            await db.close()


# on_ready cog!
def setup(bot):
    print("VoiceCog loaded!")
    bot.add_cog(VoiceCog(bot))
