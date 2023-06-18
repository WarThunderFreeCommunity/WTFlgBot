import time
import json
import asyncio

import nextcord
from nextcord.ext import tasks, application_checks
from nextcord.ext.commands import Bot, Cog

from ..extensions.DBWorkerExtension import DataBase
from ..extensions.EXFormatExtension import ex_format


TECH_IDS = None
NATION_IDS = None


class AfterKickUserButtons(nextcord.ui.View):
    def __init__(self, lang, members, message) -> None:
        super().__init__(timeout=5*60)
        self.members = members
        self.message = message
        self.data = { # TODO
            ...
        } if lang == "RU" else { 
            ...
        }
        self.close_for_all.label = "close_for_all"
        self.close_for_user.label = "close_for_user"

        self.close_for_all.disabled = True # TODO
        self.close_for_user.disabled = True # TODO

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


# TODO переписать на один класс и два наследника
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
                emoji=TECH_IDS['0'],
                value=0
            ),
            nextcord.SelectOption(
                label="Воздушные",
                description="Выбрать воздушные бои",
                emoji=TECH_IDS['1'],
                value=1
            ),
            nextcord.SelectOption(
                label="Морские",
                description="Выбрать морские бои",
                emoji=TECH_IDS['2'],
                value=2
            ),
            nextcord.SelectOption(
                label="Убрать режим",
                description="Убрать режим игры...",
                emoji=TECH_IDS['-'],
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

# TODO переписать на один класс и два наследника
class ChooseGameNationSelect(nextcord.ui.Select):
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
                label="Америка",
                description="Выбрать Америку",
                emoji="🦅",
                value=0
            ),
            nextcord.SelectOption(
                label="Советский союз",
                description="Выбрать Советский союз",
                emoji="⚒",
                value=1
            ),
            nextcord.SelectOption(
                label="Япония",
                description="Выбрать Японию",
                emoji="🍣",
                value=2
            ),
            nextcord.SelectOption(
                label="Убрать режим",
                description="Убрать режим игры...",
                emoji=TECH_IDS['-'],
                value='-'
            )
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
            "none_answer": "Ни кто не удалён..."
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
        # TODO ...
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
        self.close_channel.label = self.data["close_channel"]
        self.add_member.label = self.data["add_member"]
        self.del_member.label = self.data["del_member"]

        # TODO
        self.set_cmbr.disabled = True
        self.rename_channel.disabled = True
        self.close_channel.disabled = True
        self.add_member.disabled = True
        self.del_member.disabled = True

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

    async def update_message(self, member=None, pos=None, other=None):
        # Вызывается при изменении on_voice_state_update для канала с данным сообщением
        try:
            db = DataBase("WarThunder.db")
            await db.connect()

            # Новый человек в канале
            if pos == "in":
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
                    print(tech, nation)
                    cmbr = channel_settings[2] if channel_settings[2] else NATION_IDS['-'] 
                    channel_name = f"{tech} {nation} {self.channel.name.split(' ')[2]} {cmbr}"
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
    
    # TODO: Переделать логику для назначения дополнительных администраторов

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.green, row=2)
    async def set_cmbr(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Установка БР для голосового (только премиум)
        """
        if not await self.check_admin_rules(interaction):
            return
        # Первым делом требуется получить инфу о cmbr с бд, if None то назначаем если уже есть меняем
        # TODO: запись инфы о канале в бд
        # TODO Modal с выборов боевого рейтинга (только float, длина(len) от 1(1.0) до 4(10.7))
        ...

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
        await self.update_message(pos="name_update", other={"interaction": interaction})
        await interaction.send("Настройки применены к каналу!", ephemeral=True)
        # TODO переделать на управление правами (для доната)
        ...

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.blurple, row=3)
    async def close_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Закрывает чат для вступления других людей (только премиум)
        """
        if not await self.check_admin_rules(interaction):
            return
        # TODO переделать на управление правами (для доната)
        ...
    
    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.blurple, row=3)
    async def add_member(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Добавление людей в права канала (только премиум)
        """
        if not await self.check_admin_rules(interaction):
            return
        # TODO переделать на управление правами (для доната)
        ...
        
    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.blurple, row=3)
    async def del_member(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Удаление людей в правах канала (только премиум)
        """
        if not await self.check_admin_rules(interaction):
            return
        # TODO переделать на управление правами (для доната)
        ...
    

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
                    continue# TODO embeds
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
                await message.edit(content=None, embed=embed, view=view) # TODO embeds
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
        * self.afk_channel_id = None
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
                #  TODO Когда основной функционал будет готов и отлажен, добавить сортировку..
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
                if not (channel_save_data := await db.get_one(
                        "SELECT * FROM VoiceCogChannelsSaves WHERE creatorId=?",
                        (member.id,)
                    )):
                    await db.run_que(
                        "INSERT INTO VoiceCogChannelsSaves (creatorId) VALUES (?)",
                        (member.id,)
                    )
                    channel_name = f"❌ ❌ {channel_options[1]} ❌"
                else:
                    limit_var = channel_save_data[4] # user_limit
                    channel_name = \
                        f"{self.tech_ids[str(channel_save_data[1])] if channel_save_data[1] != None  else '❌'} " \
                        f"{self.nation_ids[str(channel_save_data[2])] if channel_save_data[2] != None  else '❌'} " \
                        f"{channel_options[1]} {channel_save_data[3] if channel_save_data[3] != None else '❌'}"
                voice_channel = await member.guild.create_voice_channel(
                    name=channel_name,
                    #position=position,  # создаём канал под последним по времени
                    category=channel_category,  # в категории канала "основы"
                    reason=f"{member.name} in '{after.channel.name}'",  # (отображается в Audit Log)
                    user_limit= 0 if not limit_var else limit_var
                )
                await member.move_to(voice_channel)
                await voice_channel.edit(sync_permissions=True)
                message = await voice_channel.send(f"{member.name} created voice")
                view = VoiceChannelsButtons(lang, member, message, voice_channel)
                embed = VoiceInfoEmbed(lang, [member.id], voice_channel)
                await message.edit(content=None, embed=embed, view=view)
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
