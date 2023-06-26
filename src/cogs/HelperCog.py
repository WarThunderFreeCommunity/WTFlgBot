import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context


class HelperCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.on_init.start()

    @tasks.loop(count=1)
    async def on_init(self):
        pass

    def cog_unload(self):
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if 'https://discord.gg/' in message.content and not message.author.guild_permissions.administrator:
            for role_allowed in [
                nextcord.utils.find(lambda r: r.id == 954393422716879019, message.guild.roles), # vip1 main
                nextcord.utils.find(lambda r: r.id == 1007965606789783572, message.guild.roles),# vip2 main
                nextcord.utils.find(lambda r: r.id == 827202390682894358, message.guild.roles), # deputy main
                nextcord.utils.find(lambda r: r.id == 812667192104583218, message.guild.roles), # head main
                nextcord.utils.find(lambda r: r.id == 1027862764322029679, message.guild.roles) # events main
            ]:
                if role_allowed in message.author.roles:
                    return
            await message.delete()
    


# on_ready cog!
def setup(bot: Bot):
    print("HelperCog loaded!")
    bot.add_cog(HelperCog(bot))
