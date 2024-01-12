import sys
import asyncio
import random
import logging
from urllib.parse import quote
from typing import List

from discord.ext.commands import Bot, Cog
from discord.ext import tasks
import discord
from bs4 import BeautifulSoup
import aiohttp

if __name__ != "__main__": # debug if...
    from core.database import get_session
    import schemas
    import services


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
CONTENT = {
    RU_NEWS_HOOK: [
            "Хей, <@&1157380814347190272>, тут свежая новость!",
            "Привет, <@&1157380814347190272>, у нас есть свежая новость!",
            "Эй, <@&1157380814347190272>, появилась новость!",
            "Здравствуйте, <@&1157380814347190272>, у нас есть актуальная новость!",
            "Приветствую, <@&1136434561002254458>! Важное объявление!",
        ],
    EN_NEWS_HOOK: [
            "Hey, <@&1157380868210438276>, here's a fresh news!",
            "Hello, <@&1157380868210438276>, we've got some fresh news!",
            "Hey, <@&1157380868210438276>, there's a new news update!",
            "Greetings, <@&1157380868210438276>! We have an exciting news to share!",
            "Hey, <@&1157380868210438276>, check out the latest news!",
        ],
    RU_CHANGES_HOOK: [
            "Хей, <@&1157380916533010452>, новое обновление!",
            "Привет, <@&1157380916533010452>, у нас есть новое обновление!",
            "Эй, <@&1157380916533010452>, тут свежее обновление!",
            "Хей, <@&1157380916533010452>, пришло новое обновление!",
            "Приветствую, <@&1157380916533010452>! У нас есть актуальное обновление!",
        ],
    EN_CHANGES_HOOK: [
            "Hey, <@&1136313556225232964>, new update!",
            "Hello, <@&1136313556225232964>, we have a new update!",
            "Hey, <@&1136313556225232964>, there's a fresh update!",
            "Greetings, <@&1136313556225232964>! We have an exciting update to share!",
            "Hey, <@&1136313556225232964>, check out the latest update!",
        ],
}


async def get_bs4(news_link: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(news_link) as response:
            if response.status == 200:
                content = await response.read()
                return BeautifulSoup(content, "html.parser")
            else:
                return None


async def get_widgets(soup: BeautifulSoup):
    news_widgets: List[BeautifulSoup] = soup.select(".showcase__item.widget")

    for widget in reversed(news_widgets):
        title = widget.select_one(".widget__title").text.strip()
        comment = widget.select_one(".widget__comment").text.strip()
        date = widget.select_one(".widget-meta__item--right").text.strip()
        news_url = "https://warthunder.com" + widget.select_one(".widget__link")["href"]
        image_url = "https:" + quote(
            widget.select_one(".widget__poster-media.js-lazy-load")["data-src"]
        )

        yield {
            "title": title,
            "comment": comment,
            "date": date,
            "news_url": news_url,
            "image_url": image_url,
        }


async def process_news(soup: BeautifulSoup):
    # Все новости состоят из:
    # <div class="content__header content__header--narrow">
    # <section class="section section--narrow">
    # <section class="section section--narrow article">
    # <section class="section section--narrow article-also">
    # <section class="section section--narrow social-sharing">
    # Создать функцию - обработчик данных частей (одну или несколько)
    # Внутри одних обработчиков могут быть другие обработчики...
    ...


def get_embed_py_preview(preview) -> discord.Embed:
    text = f"### [{preview['title']}]({preview['news_url']})\n"
    embed = discord.Embed(description=text + preview["comment"])
    embed.set_image(url=preview["image_url"])
    embed.set_footer(text=preview["date"])
    return embed


async def send_webhook(url_webhook: str, embed: discord.Embed) -> discord.Message:
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(url_webhook, session=session)
        message = await webhook.send(content=random.choice(CONTENT[url_webhook]), embed=embed, wait=True)
        return message


class WTNewsCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.update_news.start()

    async def cog_unload(self) -> None:
        self.update_news.stop()

    @tasks.loop(minutes=10)
    async def update_news(self):
        await self.bot.wait_until_ready()
        ru_channel = await self.bot.fetch_channel(1148657425046577152)
        en_channel = await self.bot.fetch_channel(1148657314912538694)

        news_links = [
            [RU_NEWS_LINK, RU_NEWS_HOOK, ru_channel],
            [EN_NEWS_LINK, EN_NEWS_HOOK, en_channel],
            [RU_CHANGES_LINK, RU_CHANGES_HOOK, ru_channel],
            [EN_CHANGES_LINK, EN_CHANGES_HOOK, en_channel],
        ]

        for link, hook, channel in news_links:
            async for db_session in get_session():
                async for preview in get_widgets(await get_bs4(link)):
                    if await services.news.get_news_by_url(db_session, preview["news_url"]):
                        continue
                    await services.news.create_news(db_session, data=schemas.NewsInDB(**preview))
                    embed = get_embed_py_preview(preview)
                    wh_msg = await send_webhook(hook, embed)
                    message = await channel.fetch_message(wh_msg.id)
                    thread = await message.create_thread(name=preview["title"])
                    await thread.send("Cooooming soooooon...")
                    await thread.edit(locked=True)
                    await asyncio.sleep(5)


async def setup(bot: Bot):
    logging.getLogger("discord.cogs.load").info("WTNewsCog loaded!")
    await bot.add_cog(WTNewsCog(bot))


async def main():
    news_link = "https://warthunder.com/ru/news/"
    async for preview in get_widgets(await get_bs4(news_link)):

        print(preview)
        print()


if __name__ == "__main__":
    asyncio.run(main())
