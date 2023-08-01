import re
import urllib.parse
import requests
import concurrent.futures
import html

import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context


def translate(text, target_language='ru', source_language='auto', timeout=5):
    #  translate(text='hello world', target_language=['en', 'ru'])
    pattern = r'(?s)class="(?:t0|result-container)">(.*?)<'
    
    def _make_request(target_language, source_language, text, timeout):
        escaped_text = urllib.parse.quote(text.encode('utf8'))
        url = 'https://translate.google.com/m?tl=%s&sl=%s&q=%s'%(target_language, source_language, escaped_text)
        response = requests.get(url, timeout=timeout)
        result = response.text.encode('utf8').decode('utf8')
        result = re.findall(pattern, result)
        if not result: raise f"{response.text}"
        return html.unescape(result[0])
    
    if len(text) > 5000:
        return False
    
    if isinstance(target_language, list):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            if (request := _make_request):
                futures = [executor.submit(request, target, source_language, text, timeout) for target in target_language]
                return [f.result() for f in futures]
            else:
                return request
             
    return _make_request(target_language, source_language, text, timeout)


def is_en_language(text: str):    
    ALPHABET_RUSSIAN = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    ALPHABET_ENGLISH = 'abcdefghijklmnopqrstuvwxyz'

    count_ru = sum(1 for char in text.lower() if char in ALPHABET_RUSSIAN)
    count_en = sum(1 for char in text.lower() if char in ALPHABET_ENGLISH)
    
    if count_ru >= count_en:
        return False
    return True


class TranslaterCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.on_init.start()
        self.message_responses = {}

    @tasks.loop(count=1)
    async def on_init(self):
        ...
        #await self.bot.sync_all_application_commands()

    def cog_unload(self):
        ...
    
    """"
    @commands.command(alias=["t"])
    async def translate(self, ctx: Context):
        await ctx.send()

    @nextcord.slash_command(guild_ids=[407187066582204427])
    async def translate(self, interaction: nextcord.Interaction):
        await interaction.send()
    """

    @Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.channel.id != 1133729915901059102:
            return
        if message.author.bot:
            return
        if message.content.isdigit() or len(message.content) < 10:
            return
        if message.content.startswith("-t"):
            return

        # Save the bot's response for this message
        response = await self.translate_and_reply(message)
        self.message_responses[message.id] = response

    @Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message):
        if before.channel.id != 1133729915901059102:
            return
        if before.author.bot:
            return
        if before.content.startswith("-t"):
            return

        # Delete the old response from the bot
        old_response = self.message_responses.get(before.id)
        if old_response:
            await old_response.edit(
                content=await self.translate_and_reply(after, get_embed=True),
                mention_author=False,
            )

    @Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        if message.channel.id != 1133729915901059102:
            return

        # Check if the deleted message had a bot response
        bot_response = self.message_responses.get(message.id)
        if bot_response:
            await bot_response.delete()
            del self.message_responses[message.id]

    async def translate_and_reply(self, message: nextcord.Message, get_embed=False):
        text = message.content.replace("@", "")
        link = "https://discordapp.com/users/"
        source_language = "en" if is_en_language(text) else "ru"
        target_language = "ru" if is_en_language(text) else "en"
        translation = translate(text, target_language, source_language)
        """ В данный момент отсылается текст
        embed = nextcord.Embed(description=f"`{target_language}:` {translation}")
        embed.set_author(
            name=message.author.name,
            url=link + str(message.author.id),
            icon_url=message.author.avatar.url,
        )""" 
        if not get_embed:
            response = await message.reply(
                f"`{target_language}:` {translation}",
                mention_author=False
            )
            return response
        return f"`{target_language}:` {translation}"


# on_ready cog!
def setup(bot: Bot):
    print("TranslaterCog loaded!")
    bot.add_cog(TranslaterCog(bot))




