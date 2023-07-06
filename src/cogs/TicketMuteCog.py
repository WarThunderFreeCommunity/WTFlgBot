import nextcord
from nextcord.ext.commands import Bot, Cog


class TicketMuteCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message_delete(self, message):
        if "ticket" in message.channel.category.name.lower():
            if any("mute" in role.name.lower() for role in message.author.roles):
                await message.channel.send(f"Message forwarded:\n{message.content}")


# on_ready cog!
def setup(bot: Bot):
    print("TicketMuteCog loaded!")
    bot.add_cog(TicketMuteCog(bot))









