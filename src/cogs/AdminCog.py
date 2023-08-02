import time
import random
import string
import datetime
from math import ceil

import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context

from ..extensions.DBWorkerExtension import DataBase
from ..extensions.EXFormatExtension import ex_format
from ..extensions.EvalExpressionAST import eval_expr

import configuration


BOT = None # объект бота
LOG_CHANNEL_ID = 1135110265390772324
SAVED_USERS = {} # сохранённые имена админов


class PunishmentUserView(nextcord.ui.View):
    def __init__(self, punishment, active_punishment=None, admin_view=None, user=None, message=None, lang="RU") -> None:
        self.punishment = punishment
        self.admin_view = admin_view
        self.user = user
        self.message = message
        super().__init__(timeout=5*60)

    async def update_message(self):
        punishment_embed = nextcord.Embed(
            description=f"{self.admin_view.type_punishment[self.punishment[2]][0]} пользователя {self.user.mention}/`{self.user.id}`",
            color=self.admin_view.type_punishment[self.punishment[2]][1]
        )
        self.admin_view.create_fields({
            "Администратор:": f"<@{self.punishment[1]}>/`{self.punishment[1]}`",
            "Номер наказания:": f"`{self.punishment[7]}`",
            "Срок наказания:": f"`{round(self.punishment[3]/60/60, 2) if self.punishment[3] else '-'} часа(ов)`",
            "Состояние наказания: ": f"`{self.admin_view.status_punishment[self.punishment[8]]}`",
            "Комментарий:": f"`{self.punishment[4]}`"
        }, punishment_embed)
        await self.message.edit(embed=punishment_embed, view=self)

    @nextcord.ui.button(label="Изменить наказание", style=nextcord.ButtonStyle.grey)
    async def edit_punishment(self, button, interaction):
        # TODO изменения мута с записью в логи!
        # send_modal
        await self.admin_view.update_message()

    @nextcord.ui.button(label="Удалить наказание", style=nextcord.ButtonStyle.grey)
    async def remove_punishment(self, button, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send("Нет прав администратора!", ephemeral=True)
        # TODO
        await self.admin_view.update_message()
    
    @nextcord.ui.button(label="Вернуться к логам", style=nextcord.ButtonStyle.grey)
    async def return_to_logs(self, button, interaction):
        await self.admin_view.update_message()
    
    async def on_timeout(self):
        try:
            for button in [self.edit_punishment, self.remove_punishment, self.return_to_logs]:
                button.disabled = True
            await self.message.edit(view=self)
        except:
            pass


class AdminUserModal(nextcord.ui.Modal):
    """Класс - родитель для создания наказаний

    Args:
        nextcord (_type_): _description_
    """
    def __init__(self, _punishmentId, user: nextcord.Member, view):
        self.punishmentId = _punishmentId
        self.user = user
        self.view = view
        self.types = {
            0: "warn",
            1: "mute",
            2: "ban!"
        }
        super().__init__(
            "Настройте наказание",
            timeout=5*60,
        )
        self.add_item(reason := nextcord.ui.TextInput(
            label="Укажите комментарий",
            placeholder="Плохое поведение",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
        ))
        if _punishmentId in [1]:
            self.add_item(punishment_time := nextcord.ui.TextInput(
                label="Укажите время наказания в часах",
                placeholder="24*7",
                style=nextcord.TextInputStyle.paragraph,
                required=True,
            ))
            self.punishment_time = punishment_time
        self.reason = reason
    
    @staticmethod
    def __generate_random_string(length=17):
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    async def callback(self, interaction: nextcord.Interaction):
        self.string_hash = self.__generate_random_string()
        self.userId = self.user.id
        self.adminId = interaction.user.id
        try:
            self.punihsmentTime = int(eval_expr(self.punishment_time.value) * 60 * 60)
        except AttributeError:
            self.punihsmentTime = None
        self.punihsmentComment = self.reason.value
        self.punihsmentSetTime = int(time.time())
        if self.punihsmentTime:
            self.punihsmentEndTime = self.punihsmentSetTime + self.punihsmentTime
        else:
            self.punihsmentEndTime = None
        self.statusId = 1
        try:
            db = DataBase("WarThunder.db")
            await db.connect()
            await db.run_que(
                "INSERT INTO AdminPunishmentUsersSaves "
                "(userId, adminId, punishmentId, punihsmentTime, "
                "punihsmentComment, punihsmentSetTime, punihsmentEndTime, "
                "randomHash, statusId)"
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self.userId, self.adminId, self.punishmentId,
                    self.punihsmentTime, self.punihsmentComment,
                    self.punihsmentSetTime, self.punihsmentEndTime,
                    self.string_hash, self.statusId
                )
            )
            embed = nextcord.Embed()
            embed.set_author(
                name=f"Наказан({self.types[self.punishmentId]}): "
                     f"{self.user.name}/{self.user.id}",
                icon_url=self.user.avatar.url,
                url="https://discordapp.com/users" + str(self.user.id),
            )
            embed.add_field(
                name="Администратор:",
                value=f"{interaction.user.mention}/`{interaction.user.name}`\n"
                    f"`{interaction.user.id}`"
            )
            embed.add_field(
                name="Номер наказания:",
                value=f"`{self.string_hash}`"
            ),
            try:
                embed.add_field(
                    name="Срок наказания:",
                    value=f"`{self.punishment_time.value} часа(ов)`"
                )
            except:
                embed.add_field(
                    name="Срок наказания:",
                    value=f"`- часа(ов)`"
                )
            embed.add_field(
                name="Комментарий:",
                value=f"`{self.punihsmentComment}`"
            )
            channel = await BOT.fetch_channel(LOG_CHANNEL_ID)
            await channel.send(embed=embed)
        except BaseException as ex:
            print(ex_format(ex, "AdminUserModal"))
        finally:
            await db.close()
            

class WarnModal(AdminUserModal):
    def __init__(self, _punishmentId, user: nextcord.Member, view):
        super().__init__(_punishmentId, user, view)

    async def callback(self, interaction: nextcord.Interaction):
        await super().callback(interaction)
        try:
            await self.user.send(
                f"```Вы получили Warn на сервер WarThunder```\n"
                f"admin: {interaction.user.mention}\ncomment: {self.punihsmentComment}"
            )
            await interaction.send("Выдан Warn!", ephemeral=True)
            self.statusId = 2
        except BaseException as ex:
            await interaction.send(f"Не удалось уведомить пользователя!", ephemeral=True)
            self.statusId = 0
        try:
            db = DataBase("WarThunder.db")
            await db.connect()
            await db.run_que(
                "UPDATE AdminPunishmentUsersSaves SET statusId=? WHERE randomHash=?",
                (self.statusId, self.string_hash)
            )
        except BaseException as ex:
            print(ex_format(ex, "WarnModal"))
        finally:
            await db.close()
        await self.view.update_message()


class MuteModal(AdminUserModal):           
    async def callback(self, interaction: nextcord.Interaction):
        await super().callback(interaction)
        try:
            db = DataBase("WarThunder.db")
            await db.connect()
            punishment_time = \
                datetime.datetime.utcnow() + \
                datetime.timedelta(seconds=self.punihsmentTime)
            await self.user.timeout(timeout=punishment_time, reason=self.punihsmentComment)
            await interaction.send("Установлен timeout!", ephemeral=True)
            self.statusId = 2 # TODO
            await db.run_que(
                "UPDATE AdminPunishmentUsersSaves SET statusId=? WHERE randomHash=?",
                (self.statusId, self.string_hash)
            )
            #current_punishment = await db.get_one(
            #    "",
            #    (...,)
            #)
            # TODO добавить перезапись наказаний если существует действующее
            #  стоит также учитывать что может не быть наказаний активных
        except BaseException as ex:
            print(ex_format(ex, "mute_modal"))
        finally:
            await db.close()
        await self.view.update_message()


class BanModal(AdminUserModal):           
    async def callback(self, interaction: nextcord.Interaction):
        await super().callback(interaction)
        try: # TODO бан постоянный 
            db = DataBase("WarThunder.db")
            await self.user.send(
                f"```Вам был выдан бан на сервере War Thunder```\n"
                f"admin: {interaction.user.mention}\ncomment: {self.punihsmentComment}"
            )
            await self.user.ban(reason=self.reason)
            await interaction.send("Выдан бан", ephemeral=True)
            await db.connect()
            ... # TODO
        except BaseException as ex:
            print(ex_format(ex, "ban_modal"))
        finally:
            await db.close()


class AdminUserView(nextcord.ui.View):
    def __init__(self, user=None, message=None, list_in_page=4, lang="RU", bot=None) -> None:
        self.user: nextcord.Member = user
        self.message = message
        super().__init__(timeout=5*60)
        self.fetch_punishment.disabled = True # TODO
        self.pages = []
        self.page_number = 0
        self.list_in_page = list_in_page
        self.type_punishment = {
            0: ["Варн", 0x096499],
            1: ["Мут", 0x0d234f],
            2: ["Бан", 0xbf1529]
        }
        self.status_punishment = {
            0: "Ошибка выполнения",
            1: "В ожидании выполнения",
            2: "Выполнено"
        }
        self.select = None
        self.on_init.start()

    def split_array(self, arr):
        arr.reverse()
        result = []
        sub_array = []
        for i in range(len(arr)):
            sub_array.append(arr[i])
            if len(sub_array) == self.list_in_page:
                result.append(sub_array)
                sub_array = []
        if sub_array:
            result.append(sub_array)
        return result

    @staticmethod
    def create_fields(fields, embed) -> None:
        for field in fields:
            embed.add_field(name=field, value=fields[field])

    @tasks.loop(count=1, reconnect=False)
    async def on_init(self):
        await self.update_message()

    # TODO  
    #  с указанием времени равному 0 и комментарию, удаление мута идёт через select с правами админа
    async def update_message(self):
        global SAVED_USERS
        self.current_page.label = f"Текущая страница: {self.page_number + 1}"
        try:
            db = DataBase("WarThunder.db")
            await db.connect()
            user_punishments = await db.get_all(
                "SELECT * FROM AdminPunishmentUsersSaves WHERE userId=?",
                (self.user.id,)
            )
            active_punishment = await db.get_one(
                "SELECT * FROM AdminPunishmentUsers WHERE userId=?",
                (self.user.id,)
            )
            main_embed = nextcord.Embed(
                description=f"Логи пользователя {self.user.mention}/`{self.user.name}`/`{self.user.id}`"
            )
            self.create_fields({
                "Варны пользователя": f"`Количество: {len([punishment for punishment in user_punishments if punishment[2] == 0])}`",
                "Муты пользователя": f"`Количество: {len([punishment for punishment in user_punishments if punishment[2] == 1])}`",
                "Баны пользователя": f"`Количество: {len([punishment for punishment in user_punishments if punishment[2] == 2])}`",
                "Страницы наказаний": f"`Количество: {ceil(len(user_punishments) / self.list_in_page)}`",
                "Активное наказание": f"`Тип и номер: {', '.join([self.type_punishment[active_punishment[2]][0], active_punishment[7]]) if active_punishment else '-'}`"
            }, main_embed)
            embeds = [main_embed]
            if len(user_punishments):
                self.pages = self.split_array(user_punishments)
                options = []
                for i,  punishment in enumerate(self.pages[self.page_number]):
                    if not (admin_name := SAVED_USERS.get(punishment[1])):
                        admin_name = (await BOT.fetch_user(punishment[1])).name
                        SAVED_USERS[punishment[1]] = admin_name
                    options.append(nextcord.SelectOption(
                        label=f"Выбрать {self.type_punishment[punishment[2]][0]} №{i + 1}",
                        description=f"Номер наказания: {punishment[7]}",
                        value=punishment[7]
                    ))
                    other_embed = nextcord.Embed(
                        description=f"Тип наказания: `{self.type_punishment[punishment[2]][0]}({i + 1})`",
                        color=self.type_punishment[punishment[2]][1]
                    )
                    self.create_fields({
                        "Администратор:": f"<@{punishment[1]}>/`{admin_name}`\n`{punishment[1]}`",
                        "Номер наказания:": f"`{punishment[7]}`",
                        "Срок наказания:": f"`{round(punishment[3] / 60 / 60, 2) if punishment[3] else '-'} часа(ов)`",
                        "Состояние наказания: ": f"`{self.status_punishment[punishment[8]]}`",
                        "Комментарий:": f"`{punishment[4]}`"
                    }, other_embed)
                    other_embed.timestamp = datetime.datetime.fromtimestamp(punishment[5])
                    embeds.append(other_embed)
                if self.select:
                    self.remove_item(self.select)
                self.select = nextcord.ui.Select(placeholder="Выберите наказание для редактирования", options=options)
                async def select_callback(interaction: nextcord.Interaction):
                    for punishment in self.pages[self.page_number]:
                        if punishment[7] == self.select.values[0]:
                            new_view = PunishmentUserView(punishment, active_punishment, self, self.user, self.message)
                            break
                    await new_view.update_message()
                self.select.callback = select_callback
                self.add_item(self.select)
            await self.message.edit(embeds=embeds, view=self)
        except BaseException as ex:
            print(ex_format(ex, "AdminUserView"))
        finally:
            await db.close()

    @nextcord.ui.button(
        label="Предыдущая страница", style=nextcord.ButtonStyle.grey, row=0
    )
    async def previous_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.page_number == 0:
            return
        self.page_number -= 1
        await self.update_message()

    @nextcord.ui.button(
        label="Текущая страница: 1", style=nextcord.ButtonStyle.grey, row=0
    )
    async def current_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.page_number == 0:
            return
        self.page_number = 0
        await self.update_message()

    @nextcord.ui.button(
        label="Следующая страница", style=nextcord.ButtonStyle.grey, row=0
    )
    async def next_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.page_number >= len(self.pages) - 1:
            return
        self.page_number += 1
        await self.update_message()
    
    @nextcord.ui.button(
        label="Выдать варн", style=nextcord.ButtonStyle.grey, row=1
    )
    async def warn_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(WarnModal(0, self.user, self))

    @nextcord.ui.button(
        label="Выдать мут", style=nextcord.ButtonStyle.grey, row=1
    )
    async def mute_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(MuteModal(1, self.user, self))

    @nextcord.ui.button(
        label="Выдать бан", style=nextcord.ButtonStyle.grey, row=1
    )
    async def ban_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(BanModal(2, self.user, self))
    
    @nextcord.ui.button(
        label="Поиск наказания по id", style=nextcord.ButtonStyle.grey, row=1
    ) # TODO ...
    async def fetch_punishment(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(...)
    
    async def on_timeout(self):
        try:
            for button in [
                self.warn_user, self.mute_user, self.ban_user, self.fetch_punishment,
                self.previous_page, self.current_page, self.next_page
            ]:
                button.disabled = True
            self.select.disabled = True
            await self.message.edit(view=self)
        except:
            pass


# TODO добавить выозов modal с поиском пользователя
class AdminInteadSlashButtons(nextcord.ui.View):
    def __init__(self, lang="RU") -> None:
        super().__init__(timeout=None, prevent_update=False)

    @nextcord.ui.button(
        label="Ввести пользователя", style=nextcord.ButtonStyle.grey, custom_id="AdminCog:AdminMainView:enter_user"
    )
    async def enter_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(...)


class AdminCog(Cog):
    def __init__(self, bot: Bot):
        global BOT
        BOT = bot
        self.bot = bot
        self.on_init.start()

    @tasks.loop(count=1, reconnect=False)
    async def on_init(self):
        await self.bot.sync_all_application_commands()

    def cog_unload(self):
        self.bot.remove_view(AdminInteadSlashButtons())

    @tasks.loop(minutes=10)
    async def update_punishment(self):
        pass
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear_cache(self, ctx: Context, user_id = None):
        global SAVED_USERS
        await ctx.reply(SAVED_USERS)
        if user_id and user_id.isdigit():
            SAVED_USERS.pop(user_id)
        else:
            SAVED_USERS = {}
        await ctx.reply(SAVED_USERS)

    # добавить выбор пользователя
    @nextcord.slash_command(guild_ids=configuration.test_guild_ids,)
    async def admin(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(name="пользователь", description="просмотреть логи пользователя")
    ):
        message = await interaction.send(embed=nextcord.Embed(title="Подготовка сообщения.."), ephemeral=True)
        await message.edit(view=AdminUserView(user=member, message=message))
    


# on_ready cog!
def setup(bot: Bot):
    print("AdminCog loaded!")
    bot.add_view(AdminInteadSlashButtons())
    bot.add_cog(AdminCog(bot))