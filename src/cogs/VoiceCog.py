import time
import json

import nextcord
from nextcord.ext import tasks
from nextcord.ext.commands import Bot, Cog

from ..extensions.DBWorkerExtension import DataBase
from ..extensions.EXFormatExtension import ex_format


class VoiceChannelsButtons(nextcord.ui.View):
    def __init__(self, lang, admin, message, channel):
        super().__init__(timeout=None)
        self.channel = channel
        self.message = message
        self.admins = [admin.id]
        self.lang = lang
        # TODO: нормальные имена забабахать
        self.data = {
            "set_cmbr": "set_cmbr",
            "set_tech": "set_tech",
            "set_limit": "set_limit",
            "kick_user": "kick_user"
        } if lang == "ru" else {
            "set_cmbr": "set_cmbr",
            "set_tech": "set_tech",
            "set_limit": "set_limit",
            "kick_user": "kick_user"
        }
        self.set_cmbr.label = self.data["set_cmbr"]
        self.set_tech.label = self.data["set_tech"]
        self.set_limit.label = self.data["set_limit"]
        self.kick_user.label = self.data["kick_user"]

    async def update_message(self, member, before=None, after=None):
        # TODO: Вызывается при изменении on_voice_state_update для канала с данным сообщением,
        #  с участием channel_id с данным view (хранить в словаре)
        # Общая логика ещё не продумана Суть в обновлении select для разных людей, можно просто 
        #  заменить кнопками
        # Сюда же можно запихнуть логику обновления админа
        print([member.name for member in self.channel.members])

    async def check_admin_rules(self, interaction: nextcord.Interaction):
        if interaction.user.id in self.admins \
        or interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("Вы не администратор", ephemeral=True)
        return False
        ...
        
    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def set_cmbr(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Установка БР для голосового
        """
        if not await self.check_admin_rules(interaction):
            return
        # TODO Модал с выборов боевого рейтинга (только float, длина от 1(1.0) до 4(10.7))
        ...
    
    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def set_tech(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Установка нации для голосового
        """
        if not await self.check_admin_rules(interaction):
            return
        # TODO Select отправляется сообщение с select и флагами стран
        ...

    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def set_limit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Установка лимита пользователей
        """
        if not await self.check_admin_rules(interaction):
            return
        
        modal = nextcord.ui.Modal("your limit...",)
        limit = nextcord.ui.TextInput(label="limit..", default_value=4)
        modal.add_item(limit)
        async def callback_fun(interaction: nextcord.Interaction):
            await interaction.channel.edit(user_limit=int(limit.value))
            await interaction.response.send_message(f"the limit is set to {limit.value}...")
        modal.callback = callback_fun
        await interaction.response.send_modal(modal)
    
    @nextcord.ui.button(label=None, style=nextcord.ButtonStyle.grey)
    async def kick_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Удаления участника из канала
        """
        if not await self.check_admin_rules(interaction):
            return
        
        # TODO отправляется select со списком юзеров в канале, после кика появляется кнопка запрета
        #  участнику на вход и установкой ограничения для канала
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
        self.on_init.start()
        self.update_consts.start()

    @tasks.loop(count=1, reconnect=False)
    async def on_init(self):
        # TODO: чекер каналов активных
        # TODO: Изменение сообщений в старых каналах (или удаление или перезапись но новые view)
        ...

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
            for constant in ["smiles_channel", "afk_channel_id", "parrent_channel_ids"]:
                temp = await db.get_one(
                    "SELECT constantValue FROM VoiceCogConstants WHERE constantName=?",
                    (constant,),
                )
                setattr(self, constant, json.loads(temp[0]))
        except BaseException as ex:
            ex_format(ex, "update_consts")
        finally:
            await db.close()

    @Cog.listener()
    async def on_voice_state_update(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ): # TODO: Всё это дело можно разнести по разным функциям, дабы не городить 100500 вложенностей
        try:
            db = DataBase("WarThunder.db")
            await db.connect()

            # Updating view in channel
            if before.channel and before.channel.id in self.channel_views:
                await self.channel_views[before.channel.id].update_message(member, before)
            if after.channel and after.channel.id in self.channel_views:
                await self.channel_views[after.channel.id].update_message(member, after=after)

            # Connected to creater new channel (channel with ➕ in name)
            if after.channel and (str(after.channel.id) in self.parrent_channel_ids):
                # Поиск последнего канала в категории (сортировка, заключается в распределении между None и creater channel)
                channel_type = self.parrent_channel_ids[str(after.channel.id)].split(':')
                position = None if channel_type[3] == '-' else nextcord.utils.get(
                    member.guild.voice_channels, id=int(channel_type[3])
                ).position
                afk_channel = nextcord.utils.get(
                    member.guild.voice_channels, id=int(self.afk_channel_id)
                )
                # TODO: Костыль для того, чтоб очумелые ручки не успевали выходить из канала до создания нового
                await member.move_to(afk_channel)
                voice_channel = await member.guild.create_voice_channel(
                    name=f"{after.channel.name.replace(self.smiles_channel[0], f'{self.smiles_channel[1]} ')}",
                    position=position,  # создаём канал под последним по времени
                    category=after.channel.category,  # в категории канала "основы"
                    reason=f"{member.name} in '{after.channel.name}'",  # (отображается в Audit Log)
                )
                await member.move_to(voice_channel)
                message = await voice_channel.send(f"{member.name} created voice") # TODO: embeds
                view = VoiceChannelsButtons("ru", member, message, voice_channel) # TODO: языки
                await message.edit(view=view)
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
