import asyncio
from urllib.parse import quote
from typing import List

from bs4 import BeautifulSoup
import aiohttp


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

    for widget in news_widgets:
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


async def main():
    news_link = "https://warthunder.com/ru/news/"
    async for preview in get_widgets(await get_bs4(news_link)):

        print(preview)
        print()


if __name__ == "__main__":
    asyncio.run(main())
