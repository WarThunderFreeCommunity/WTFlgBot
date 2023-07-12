import nextcord
from nextcord.ext.commands import Bot, Cog


class TicketMuteCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        try:
            if "ticket" in message.channel.category.name.lower() and any(
                "mute" in role.name.lower() for role in message.author.roles
            ):
                async with message.channel.typing():
                    author = message.author
                    embed = nextcord.Embed(description=message.content[:4096])
                    embed.set_author(
                        name=author.name,
                        url=f"https://discord.com/users/{author.id}",
                        icon_url=author.avatar.url,
                    )
                    if len(message.content) > 4096:
                        embed.set_footer(text="Note: max message length - 4096...")
                if message.reference:
                    reference_message = await message.channel.fetch_message(
                        message.reference.message_id
                    )
                    new_message = await reference_message.reply(embed=embed)
                else:
                    new_message = await message.channel.send(embed=embed)
                if message.attachments:
                    files = []
                    thread = await new_message.create_thread(name="Attachments ➡")
                    async with thread.typing():
                        for attachment in message.attachments:
                            attachment_file = await attachment.to_file()
                            files.append(attachment_file)
                    await thread.send(files=files)
        except AttributeError:
            pass


# on_ready cog!
def setup(bot: Bot):
    print("TicketMuteCog loaded!")
    bot.add_cog(TicketMuteCog(bot))
