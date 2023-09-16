import re
import urllib.parse
import requests
import concurrent.futures
import html
from urllib.parse import urlparse

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
        self.finded_users = {}
        self.ignore_my_message_id = []
        self.message_responses = {}

    @tasks.loop(count=1)
    async def on_init(self):
        ...
        #await self.bot.sync_all_application_commands()

    def cog_unload(self):
        ...
    
    async def text_processing(self, text: str):      
        # links
        #re.sub(r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*$', "", text)
        def remove_urls(_text):
            words = _text.split()
            without_urls = [word for word in words if not urlparse(word).scheme]
            return ' '.join(without_urls)
        text = remove_urls(text)

        # mentions
        mentions = re.findall(r'<@(\d+)>', text)
        for mention in mentions:
            user_id = int(mention)               
            if user_id in self.finded_users:
                name = self.finded_users[user_id]
            else:
                name = (await self.bot.fetch_user(user_id)).name 
                self.finded_users[user_id] = name
            text = text.replace(f'<@{mention}>', name)

        # stickers
        text = re.sub(r"<[^:\s]+>", "", text)
        text = re.sub(r":[^:\s]+:", "", text)
        text = re.sub(r'<(\d+)>', "",  text)
        text = text.replace("-t", "")
        
        return text

    @commands.command(aliases=["tig"])
    async def tignore(self, ctx: Context):
        if ctx.author.id in self.ignore_my_message_id:
            self.ignore_my_message_id.remove(ctx.author.id)
            await ctx.reply("unignore translations", mention_author=False)
        else: 
            self.ignore_my_message_id.append(ctx.author.id)
            await ctx.reply("ignore translations", mention_author=False)

    @Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.channel.id != 1141398986725540092:#1133729915901059102:
            return
        if message.author.bot:
            return
        if message.author.id in self.ignore_my_message_id and \
        not message.content.startswith("-t"):
            return
        if message.content.isdigit() or len(message.content) < 10:
            return
        if message.content.startswith("-t") and \
        message.author.id not in self.ignore_my_message_id:
            return
        if message.content.startswith(">"):
            return
        
        if response := await self.translate_and_reply(message):
            self.message_responses[message.id] = response

    @Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message):
        if before.channel.id != 1141398986725540092:#1133729915901059102:
            return
        if before.author.bot:
            return
        if before.author.id in self.ignore_my_message_id and \
        not before.content.startswith("-t"):
            return
        if before.content.startswith("-t") and \
        before.author.id not in self.ignore_my_message_id:
            return

        # Delete the old response from the bot
        old_response = self.message_responses.get(before.id)
        if old_response:
            await old_response.edit(
                content=await self.translate_and_reply(after, get_embed=True),
            )

    @Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        if message.channel.id != 1141398986725540092:#1133729915901059102:
            return

        # Check if the deleted message had a bot response
        bot_response = self.message_responses.get(message.id)
        if bot_response:
            await bot_response.delete()
            del self.message_responses[message.id]

    async def translate_and_reply(self, message: nextcord.Message, get_embed=False):
        text = await self.text_processing(message.content)
        if len(text) < 10: return False
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




