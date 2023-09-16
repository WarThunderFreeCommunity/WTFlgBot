import re
import json
import asyncio
import random
from urllib.parse import quote
from typing import List

import aiohttp
import requests
import nextcord
from bs4 import BeautifulSoup
import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context

from ..extensions.DBWorkerExtension import DataBase
from ..extensions.EXFormatExtension import ex_format


RU_NEWS_LINK = "https://warthunder.com/ru/news/"
EN_NEWS_LINK = "https://warthunder.com/en/news/"
RU_CHANGES_LINK = "https://warthunder.com/ru/game/changelog/"
EN_CHANGES_LINK = "https://warthunder.com/en/game/changelog/"
RU_NEWS_HOOK = "https://discord.com/api/webhooks/1148658847095988274/XEAhTLAE8ljAAPA6h3WE-3Qs9ZHvFhkn8c0lzRUuAJXw5olQUCU6CsV48HuWScPUTXtX"
EN_NEWS_HOOK = "https://discord.com/api/webhooks/1148658458468557043/OISfx157G9eL1t931BSS_x8rOv5hjUeM3VQpV7dFYvAugShTH5RNJ_1aNA9twtHzBvl5"
RU_CHANGES_HOOK = "https://discord.com/api/webhooks/1148658852011708447/TvMvxg5egZnGkGcE-PEkJ3Oclpl7ONOBWo2CVoWK13j1xGlZVSDurD0UWVKfbVnPfAGH"
EN_CHANGES_HOOK = "https://discord.com/api/webhooks/1148658467708600381/BBFPfvUE3fA4J2den3qBbB7guBpjaznct3iKrkJKGLVdAHTD_WTxjqGNn1Nm51l1QbIF"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
]
""""
TYPES_NEWS =>
0 - RU_NEWS_LINK
1 - EN_NEWS_LINK

2 - RU_CHANGES_LINK
3 - EN_CHANGES_LINK

"""


async def get_news_from_page(url, url_webhook, type_, ctx, title_text):
    if not url_webhook:
        return

    response = requests.get(url, headers={"User-Agent": random.choice(USER_AGENTS),})

    if response.status_code != 200:
        raise Exception(f"Ошибка при получении страницы. Код ошибки: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    news_blocks: List[BeautifulSoup] = soup.find_all(class_='showcase__item widget')
    
    try:
        db = DataBase("WarThunder.db")
        await db.connect()
        title_arrays = await db.get_one(
            "SELECT titleArray FROM WTNewsCog WHERE typeNews=?",
            (type_,)
        )
        if not title_arrays:
            title_arrays = []
            await db.run_que(
                "INSERT INTO WTNewsCog (titleArray, typeNews) VALUES (?, ?)",
                ("[]", type_)
            )
        else:
            title_arrays = json.loads(title_arrays[0])
    except BaseException as ex:
        print(ex_format(ex, "WTNEWS_START"))
    finally:
        await db.close()
    
        for block in news_blocks[::-1]:
            try:
                title = block.find(class_='widget__title').text.strip()
                banner_url = "https:" + quote(block.find(
                    class_='widget__poster-media js-lazy-load'
                )['data-src'])
                comment = block.find(class_='widget__comment').text.strip()
                data = block.find(class_='widget-meta__item widget-meta__item--right').text.strip()
                more_url = "https://warthunder.com" + block.find(class_='widget__link')['href']
                
                # Для тестов
                if title_text:
                    print(title_text)
                    print(title)
                    print()
                    print(title_text not in title)
                    if title_text not in title:
                        continue
                
                if title in title_arrays:
                    continue
                title_arrays.append(title)

                response = requests.get(more_url)
                if response.status_code != 200:
                    raise Exception(f"Ошибка при получении страницы. Код ошибки: {response.status_code}")

                soup = BeautifulSoup(response.content, 'html.parser')
                p_tags = soup.find_all('p')
                #h2_tags = soup.find_all('h2')
                #all_tags = soup.find_all(['h2', 'p'])

                text_arrays = []
                news_cl = soup.find_all('div', class_='g-col')
                for element in news_cl:
                    if not element.find_all('p'):
                        continue
                
                description = p_tags[0].text.strip()
                if url_webhook in [RU_CHANGES_HOOK, EN_CHANGES_HOOK]:
                    description = comment
                if len(description) > 2000:
                    description = description[:1997] + "..."
                content = {
                    RU_NEWS_HOOK: random.choice([
                        "Хей, <@&1136434561002254458>, тут свежая новость!",
                        "Привет, <@&1136434561002254458>, у нас есть свежая новость!",
                        "Эй, <@&1136434561002254458>, появилась новость!",
                        "Здравствуйте, <@&1136434561002254458>, у нас есть актуальная новость!",
                        "Приветствую, <@&1136434561002254458>! Важное объявление!"
                    ]),
                    EN_NEWS_HOOK: random.choice([
                        "Hey, <@&1136313491184160788>, here's a fresh news!",
                        "Hello, <@&1136313491184160788>, we've got some fresh news!",
                        "Hey, <@&1136313491184160788>, there's a new news update!",
                        "Greetings, <@&1136313491184160788>! We have an exciting news to share!",
                        "Hey, <@&1136313491184160788>, check out the latest news!"
                    ]),
                    RU_CHANGES_HOOK: random.choice([
                        "Хей, <@&1136434648122142770>, новое обновление!",
                        "Привет, <@&1136434648122142770>, у нас есть новое обновление!",
                        "Эй, <@&1136434648122142770>, тут свежее обновление!",
                        "Хей, <@&1136434648122142770>, пришло новое обновление!",
                        "Приветствую, <@&1136434648122142770>! У нас есть актуальное обновление!"
                    ]),
                    EN_CHANGES_HOOK: random.choice([
                        "Hey, <@&1136313556225232964>, new update!",
                        "Hello, <@&1136313556225232964>, we have a new update!",
                        "Hey, <@&1136313556225232964>, there's a fresh update!",
                        "Greetings, <@&1136313556225232964>! We have an exciting update to share!",
                        "Hey, <@&1136313556225232964>, check out the latest update!"
                    ]),
                }
                
                embed = nextcord.Embed(description=description)
                embed.set_author(name=title, url=more_url)
                embed.set_image(banner_url)
                embed.set_footer(text=data)

                async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(url_webhook, session=session)
                    message = await webhook.send(content=content[url_webhook], embed=embed, wait=True)
                    yield {"message_id": message.id, "text_arrays": text_arrays, "title": title}
            
            except BaseException as ex:
                print(ex_format(ex, "main_for_wtnews"))

    try:
        db = DataBase("WarThunder.db")
        await db.connect()
        await db.run_que(
            "UPDATE WTNewsCog SET titleArray=? WHERE typeNews=?",
            (json.dumps(title_arrays), type_)
        )
    except BaseException as ex:
        print(ex_format(ex, "WTNEWS_START"))
    finally:
        await db.close()



class WTNewsCog(Cog):
    def __init__(self, bot: Bot):
        # send(suppress_embeds=True)
        self.bot = bot
        self.on_init.start()
        self.update_news.start()
    
    @tasks.loop(count=1, reconnect=False)
    async def on_init(self):
        #await self.bot.sync_all_application_commands()
        ...

    def cog_unload(self):
        ...

    @tasks.loop(minutes=30)
    async def update_news(self):
        links = [RU_NEWS_LINK, EN_NEWS_LINK, RU_CHANGES_LINK, EN_CHANGES_LINK]
        hoocks = [RU_NEWS_HOOK, EN_NEWS_HOOK, RU_CHANGES_HOOK, EN_CHANGES_HOOK]
        channels = [1148657425046577152, 1148657314912538694] * 2
        types = [0, 1, 2, 3, 4]
        for link, hoock, type_, channel_id in zip(links, hoocks, types, channels):
            async for result in get_news_from_page(link, hoock, type_, None, None):
                channel = await self.bot.fetch_channel(channel_id)
                message: nextcord.Message = \
                    await channel.fetch_message(result["message_id"])
                thread = await message.create_thread(
                    name=result["title"], auto_archive_duration=10080
                )
                await thread.send("coming soon...")
                for message in result["text_arrays"]:
                    await thread.send(message, suppress_embeds=True)
                await thread.edit(locked=True)

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.channel.id != 1136034295715213434:
            return
        if message.author.id == 1113954512298836071:
            return
        if message.author.id != 1136034417463263232:
            return
        await message.reply("<@&1136315037745692732>")
       
    @commands.command()
    async def news(self, ctx: Context, db_delete=False, title_text=None):
        if ctx.author.id != 1120793294931234958: return
        links = [RU_NEWS_LINK, EN_NEWS_LINK, RU_CHANGES_LINK, EN_CHANGES_LINK]
        hoocks = [RU_NEWS_HOOK, EN_NEWS_HOOK, RU_CHANGES_HOOK, EN_CHANGES_HOOK]
        channels = [1148657425046577152, 1148657314912538694] * 2
        types = [0, 1, 2, 3, 4]
        await ctx.send("Started")
        if db_delete:
            await ctx.send("db deleted news")
            try:
                db = DataBase("WarThunder.db")
                await db.connect()
                await db.run_que(
                    "DELETE FROM WTNewsCog"
                )
            except: pass
            finally:
                await db.close()
        for link, hoock, type_, channel_id in zip(links, hoocks, types, channels):
            async for result in get_news_from_page(link, hoock, type_, ctx, title_text):
                channel = await self.bot.fetch_channel(channel_id)
                message: nextcord.Message = \
                    await ctx.channel.fetch_message(result["message_id"])
                thread = await message.create_thread(
                    name=result["title"], auto_archive_duration=10080
                )
                await thread.send("coming soon...")
                for message in result["text_arrays"]:
                    await thread.send(message, suppress_embeds=True)
                await thread.edit(locked=True)
        await ctx.send("Finished")



# on_ready cog!
def setup(bot: Bot):
    print("WTNewsCog loaded!")
    bot.add_cog(WTNewsCog(bot))




