import nextcord
from nextcord.ext import tasks
from nextcord.ext.commands import Bot, Cog

from ..extensions.EXFormatExtension import ex_format


class ServerStatsCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.on_init.start()
        self.online_members.start()

    @tasks.loop(count=1)
    async def on_init(self):
        pass

    def cog_unload(self):
        self.online_members.stop()
        pass

    @tasks.loop(minutes=6)
    async def online_members(self):
        try:
            voice_members = set()
            mbrs = self.bot.get_guild(1141373361063198822).members
            online = len(list(filter(lambda x: x.status == nextcord.Status.online, mbrs)))
            idle = len(list(filter(lambda x: x.status == nextcord.Status.idle, mbrs)))
            dnd = len(list(filter(lambda x: x.status == nextcord.Status.dnd, mbrs)))
            all_online = online+idle+dnd
            for voice in self.bot.get_guild(1141373361063198822).voice_channels:
                for member in voice.members:
                    voice_members.add(member.id)
            voices_online = len(voice_members)
            await self.bot.get_channel(int(1148656018692243456)).edit(name=f'👥〡members-{len(mbrs)}')
            await self.bot.get_channel(int(1148656037839257700)).edit(name=f'🟢〡online-{all_online}')
            await self.bot.get_channel(int(1148656056289992795)).edit(name=f'🔊〡in-voices-{voices_online}')
        except BaseException as ex:
            print(ex_format(ex, "server-stats"))


# on_ready cog!
def setup(bot: Bot):
    print("ServerStatsCog loaded!")
    bot.add_cog(ServerStatsCog(bot))
