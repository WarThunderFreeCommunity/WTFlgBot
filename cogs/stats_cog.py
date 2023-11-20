import logging

import discord
from discord.ext import tasks
from discord.ext.commands import Bot, Cog


class ServerStatsCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_load(self):
        self.online_members.start()
        
    async def cog_unload(self):
        self.online_members.stop()

    @tasks.loop(minutes=6)
    async def online_members(self):
        try:
            voice_members = set()
            guild_id = 1141373361063198822
            guild = self.bot.get_guild(guild_id)

            if guild:
                # Исключаем ботов из списка участников
                mbrs = [member for member in guild.members if not member.bot]

                online = len([member for member in mbrs if member.status == discord.Status.online])
                idle = len([member for member in mbrs if member.status == discord.Status.idle])
                dnd = len([member for member in mbrs if member.status == discord.Status.dnd])
                all_online = online + idle + dnd

                for voice_channel in guild.voice_channels:
                    for member in voice_channel.members:
                        voice_members.add(member.id)

                voices_online = len(voice_members)

                # Используем метод get_channel из класса TextChannel
                await self.bot.get_channel(1148656018692243456).edit(name=f'👥〡members-{len(mbrs)}')
                await self.bot.get_channel(1148656037839257700).edit(name=f'🟢〡online-{all_online}')
                await self.bot.get_channel(1148656056289992795).edit(name=f'🔊〡ins-voices-{voices_online}')
        except Exception as ex:
            logging.getLogger("discord.cogs.stats_cog").error(ex)

    
    @online_members.before_loop
    async def before_online_members(self):
        logging.getLogger("discord.cogs.stats_cog").info("waiting..")
        await self.bot.wait_until_ready()

async def setup(bot: Bot):
    logging.getLogger("discord.cogs.load").info("ServerStatsCog loaded!")
    await bot.add_cog(ServerStatsCog(bot))
